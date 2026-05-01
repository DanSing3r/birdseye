"""Generate a static HTML page from a list of bird species with photos."""

import os
from html import escape


def generate_site(species: list[dict], checklist_url: str, *, location: str = "", date: str = "", output_dir: str = "docs") -> str:
    """
    Generate a self-contained HTML page with a responsive grid of species cards.

    Returns the path to the generated HTML file.
    """
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "index.html")

    cards_html = []
    for bird in species:
        name = escape(bird["name"])
        sci_name = escape(bird.get("sci_name", ""))
        count = escape(str(bird["count"]) if bird["count"] else "X")
        photo_url = bird.get("photo_url")
        code = bird.get("code", "")

        if photo_url:
            img = f'<img src="{escape(photo_url)}" alt="{name}" loading="lazy">'
        else:
            img = f'<div class="no-photo">No photo available</div>'

        sci_line = f'<p class="sci">{sci_name}</p>' if sci_name else ""

        if code:
            species_url = escape(f"https://ebird.org/species/{code}")
            card_open = f'<a class="card" href="{species_url}" target="_blank" rel="noopener">'
            card_close = "</a>"
        else:
            card_open = '<div class="card">'
            card_close = "</div>"

        cards_html.append(f"""      {card_open}
        {img}
        <div class="info">
          <h2>{name}</h2>
          {sci_line}
          <p>Count: {count}</p>
        </div>
      {card_close}""")

    cards = "\n".join(cards_html)
    checklist_escaped = escape(checklist_url)

    title = location if location else "Bird Checklist"
    description_parts = []
    if date:
        description_parts.append(date)
    description_parts.append(f"{len(species)} species")
    description = " · ".join(description_parts)

    og_image = next((b["photo_url"] for b in species if b.get("photo_url")), None)
    og_image_tag = f'\n  <meta property="og:image" content="{escape(og_image)}">' if og_image else ""

    favicon = '<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>%F0%9F%90%A6</text></svg>">'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  {favicon}
  <meta property="og:title" content="{escape(title)}">
  <meta property="og:description" content="{escape(description)}">
  <meta property="og:type" content="website">{og_image_tag}
  <meta name="twitter:card" content="summary_large_image">
  <meta name="description" content="{escape(description)}">
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f5f5f5; color: #333; }}
    header {{ background: #2d5016; color: white; padding: 1.5rem; text-align: center; }}
    header h1 {{ font-size: 1.5rem; margin-bottom: 0.5rem; }}
    header a {{ color: #b8d4a0; }}
    header p {{ font-size: 0.9rem; opacity: 0.9; }}
    .grid {{ columns: 3; column-gap: 1rem; padding: 1.5rem; max-width: 1200px; margin: 0 auto; }}
    @media (max-width: 900px) {{ .grid {{ columns: 2; }} }}
    @media (max-width: 500px) {{ .grid {{ columns: 1; }} }}
    .card {{ display: block; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); break-inside: avoid; margin-bottom: 1rem; transition: transform 0.2s, box-shadow 0.2s; color: inherit; text-decoration: none; }}
    .card:hover {{ transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }}
    .card:hover .info h2 {{ color: #2d5016; }}
    .card img {{ width: 100%; display: block; }}
    .no-photo {{ width: 100%; height: 220px; background: #e0e0e0; display: flex; align-items: center; justify-content: center; color: #999; font-size: 0.9rem; }}
    .info {{ padding: 0.75rem 1rem; }}
    .info h2 {{ font-size: 1.1rem; margin-bottom: 0.15rem; transition: color 0.15s; }}
    .info .sci {{ font-size: 0.8rem; font-style: italic; color: #999; margin-bottom: 0.15rem; }}
    .info p {{ font-size: 0.85rem; color: #666; }}
  </style>
</head>
<body>
  <header>
    <h1>{escape(location) if location else 'Bird Checklist'}</h1>
    <p>{escape(date) + ' &middot; ' if date else ''}{len(species)} species &middot; <a href="{checklist_escaped}">View on eBird</a></p>
  </header>
  <div class="grid">
{cards}
  </div>
</body>
</html>
"""

    with open(output_path, "w") as f:
        f.write(html)

    return output_path
