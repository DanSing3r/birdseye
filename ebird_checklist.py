#!/usr/bin/env python3
"""
Fetch bird species from an eBird checklist URL and display with common names.

Requires an eBird API key. Get one at: https://ebird.org/api/keygen
"""

import re
import sys
import requests
from urllib.parse import urlparse


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


def get_taxonomy(api_key: str) -> dict[str, str]:
    """Fetch eBird taxonomy and return a mapping of species code to common name."""
    url = "https://api.ebird.org/v2/ref/taxonomy/ebird"
    headers = {"X-eBirdApiToken": api_key}
    params = {"fmt": "json"}

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    taxonomy = response.json()
    return {species["speciesCode"]: species["comName"] for species in taxonomy}


def get_checklist(api_key: str, checklist_id: str) -> dict:
    """Fetch checklist data from eBird API."""
    url = f"https://api.ebird.org/v2/product/checklist/view/{checklist_id}"
    headers = {"X-eBirdApiToken": api_key}

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.json()


def get_checklist_species(api_key: str, checklist_url: str) -> list[dict]:
    """
    Get species from an eBird checklist with their common names.

    Returns a list of dicts with 'code', 'name', and 'count' keys.
    """
    checklist_id = extract_checklist_id(checklist_url)

    # Fetch taxonomy for code-to-name mapping
    taxonomy = get_taxonomy(api_key)

    # Fetch the checklist
    checklist = get_checklist(api_key, checklist_id)

    species_list = []
    for obs in checklist.get("obs", []):
        code = obs.get("speciesCode", "")
        name = taxonomy.get(code, code)  # Fall back to code if name not found
        count = obs.get("howManyAtleast", obs.get("howManyAtmost", "X"))

        species_list.append({
            "code": code,
            "name": name,
            "count": count
        })

    return species_list


def main():
    if len(sys.argv) < 3:
        print("Usage: python ebird_checklist.py <API_KEY> <CHECKLIST_URL>")
        print("\nGet an API key at: https://ebird.org/api/keygen")
        print("Example: python ebird_checklist.py abc123 https://ebird.org/checklist/S123456789")
        sys.exit(1)

    api_key = sys.argv[1]
    checklist_url = sys.argv[2]

    try:
        species = get_checklist_species(api_key, checklist_url)

        print(f"\nChecklist: {checklist_url}")
        print(f"Species count: {len(species)}\n")
        print(f"{'Count':<8} {'Code':<10} {'Common Name'}")
        print("-" * 60)

        for bird in species:
            count = str(bird["count"]) if bird["count"] else "X"
            print(f"{count:<8} {bird['code']:<10} {bird['name']}")

    except requests.HTTPError as e:
        print(f"API error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
