#!/usr/bin/env python3
"""
Fetch bird species from an eBird checklist URL and display with common names.

Requires an eBird API key. Get one at: https://ebird.org/api/keygen
"""

import os
import re
import sys
from datetime import datetime
import requests
from urllib.parse import urlparse, quote


def extract_checklist_id(url: str) -> str:
    """Extract the checklist ID from an eBird checklist URL."""
    # Handle URLs like:
    # https://ebird.org/checklist/S123456789
    # https://ebird.org/region/checklist/S123456789
    parsed = urlparse(url)
    path = parsed.path

    # Look for pattern like S followed by digits
    match = re.search(r'(S\d+)', path)
    if match:
        return match.group(1)

    raise ValueError(f"Could not extract checklist ID from URL: {url}")


def get_taxonomy(api_key: str) -> dict[str, dict]:
    """Fetch eBird taxonomy and return a mapping of species code to name info."""
    url = "https://api.ebird.org/v2/ref/taxonomy/ebird"
    headers = {"X-eBirdApiToken": api_key}
    params = {"fmt": "json"}

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    taxonomy = response.json()
    return {
        s["speciesCode"]: {"name": s["comName"], "sci_name": s.get("sciName", "")}
        for s in taxonomy
    }


def get_species_photo(name: str) -> str | None:
    """Fetch a photo URL for a species from the Wikipedia REST API."""
    encoded = quote(name.replace(" ", "_"))
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}"
    headers = {"User-Agent": "birdseye/0.1 (https://github.com; bird checklist tool)"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if "originalimage" in data:
            return data["originalimage"]["source"]
        if "thumbnail" in data:
            return data["thumbnail"]["source"]
    except (requests.RequestException, KeyError):
        pass
    return None


def get_checklist(api_key: str, checklist_id: str) -> dict:
    """Fetch checklist data from eBird API."""
    url = f"https://api.ebird.org/v2/product/checklist/view/{checklist_id}"
    headers = {"X-eBirdApiToken": api_key}

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.json()


def get_location_name(api_key: str, loc_id: str) -> str | None:
    """Look up a location name from its eBird location ID."""
    url = f"https://api.ebird.org/v2/ref/hotspot/info/{loc_id}"
    headers = {"X-eBirdApiToken": api_key}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get("name")
    except requests.RequestException:
        return None


def format_date(obs_dt: str) -> str:
    """Format an eBird obsDt string like '2026-02-07 14:30' into 'February 7, 2026'."""
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(obs_dt, fmt).strftime("%B %-d, %Y")
        except ValueError:
            continue
    return obs_dt


def get_checklist_species(api_key: str, checklist_url: str) -> dict:
    """
    Get species from an eBird checklist with their common names.

    Returns a dict with 'species' (list), 'location', and 'date' keys.
    """
    checklist_id = extract_checklist_id(checklist_url)

    # Fetch taxonomy for code-to-name mapping
    taxonomy = get_taxonomy(api_key)

    # Fetch the checklist
    checklist = get_checklist(api_key, checklist_id)

    loc_id = checklist.get("locId", "")
    location = checklist.get("locName") or get_location_name(api_key, loc_id) or "Unknown Location"
    date = format_date(checklist.get("obsDt", ""))

    species_list = []
    for obs in checklist.get("obs", []):
        code = obs.get("speciesCode", "")
        info = taxonomy.get(code, {"name": code, "sci_name": ""})
        name = info["name"]
        sci_name = info["sci_name"]
        count = obs.get("howManyAtleast", obs.get("howManyAtmost", "X"))

        photo_url = get_species_photo(name)

        species_list.append({
            "code": code,
            "name": name,
            "sci_name": sci_name,
            "count": count,
            "photo_url": photo_url,
        })

    return {
        "species": species_list,
        "location": location,
        "date": date,
    }


def load_api_key() -> str | None:
    """Load eBird API key from .env file or environment variable."""
    # Check environment variable first
    key = os.environ.get("EBIRD_API_KEY")
    if key:
        return key

    # Try .env file in project root
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("EBIRD_API_KEY="):
                    return line.split("=", 1)[1].strip()

    return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python ebird_checklist.py <CHECKLIST_URL>")
        print("\nSet your API key in .env (EBIRD_API_KEY=xxx) or as an environment variable.")
        print("Get an API key at: https://ebird.org/api/keygen")
        sys.exit(1)

    api_key = load_api_key()
    if not api_key:
        print("Error: No API key found.")
        print("Create a .env file with: EBIRD_API_KEY=your_key_here")
        print("Or set the EBIRD_API_KEY environment variable.")
        sys.exit(1)

    checklist_url = sys.argv[1]

    try:
        result = get_checklist_species(api_key, checklist_url)
        species = result["species"]
        location = result["location"]
        date = result["date"]

        print(f"\n{location} — {date}")
        print(f"Species count: {len(species)}\n")
        print(f"{'Count':<8} {'Code':<10} {'Common Name'}")
        print("-" * 60)

        for bird in species:
            count = str(bird["count"]) if bird["count"] else "X"
            photo = "+" if bird.get("photo_url") else "-"
            print(f"{count:<8} {bird['code']:<10} {bird['name']}  [{photo} photo]")

        from generate_site import generate_site
        output_path = generate_site(species, checklist_url, location=location, date=date)
        print(f"\nGenerated site: {output_path}")
        print("To share: push to GitHub and enable Pages (serve from docs/ on main branch).")

    except requests.HTTPError as e:
        print(f"API error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
