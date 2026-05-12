# birdseye

Turn an [eBird](https://ebird.org) checklist into a shareable static webpage — a responsive grid of species cards with photos, scientific names, and counts. Each card links to the species' eBird profile.

## Setup

Requires Python 3.12+.

```sh
uv sync
```

Get an eBird API key at https://ebird.org/api/keygen and put it in a `.env` file at the project root:

```
EBIRD_API_KEY=your_key_here
```

Or export it as `EBIRD_API_KEY` in your environment.

## Usage

```sh
python ebird_checklist.py <CHECKLIST_URL>
```

For example:

```sh
python ebird_checklist.py https://ebird.org/checklist/S123456789
```

The script fetches the checklist from eBird, looks up a photo for each species from Wikipedia, prints a summary to the terminal, and writes a self-contained HTML page to `docs/index.html`.

## Publishing

The `docs/` output is set up for GitHub Pages — push to GitHub and enable Pages serving from the `docs/` folder on the `main` branch.

To preview locally:

```sh
open docs/index.html
```

Or serve over HTTP:

```sh
python3 -m http.server -d docs 8000
```

## Files

- `ebird_checklist.py` — fetches the checklist and species data
- `generate_site.py` — renders the HTML page
- `docs/` — generated output (committed for GitHub Pages)
