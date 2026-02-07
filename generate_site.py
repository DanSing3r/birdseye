"""Generate a static HTML page from a list of bird species with photos."""

import os
from html import escape


def generate_site(species: list[dict], checklist_url: str, output_dir: str = "docs") -> str:
    """
    Generate a self-contained HTML page with a responsive grid of species cards.

    Returns the path to the generated HTML file.
    """
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "index.html")

    cards_html = []
    for bird in species:
        name = escape(bird["name"])
        count = escape(str(bird["count"]) if bird["count"] else "X")
        photo_url = bird.get("photo_url")

        if photo_url:
            img = f'<img src="{escape(photo_url)}" alt="{name}" loading="lazy">'
        else:
            img = f'<div class="no-photo">No photo available</div>'

        cards_html.append(f"""      <div class="card">
        {img}
        <div class="info">
          <h2>{name}</h2>
          <p>Count: {count}</p>
        </div>
      </div>""")

    cards = "\n".join(cards_html)
    checklist_escaped = escape(checklist_url)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Bird Checklist</title>
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
    .card {{ background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); break-inside: avoid; margin-bottom: 1rem; transition: transform 0.2s; }}
    .card:hover {{ transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }}
    .card img {{ width: 100%; display: block; }}
    .no-photo {{ width: 100%; height: 220px; background: #e0e0e0; display: flex; align-items: center; justify-content: center; color: #999; font-size: 0.9rem; }}
    .info {{ padding: 0.75rem 1rem; }}
    .info h2 {{ font-size: 1.1rem; margin-bottom: 0.25rem; }}
    .info p {{ font-size: 0.85rem; color: #666; }}
  </style>
</head>
<body>
  <header>
    <h1>Bird Checklist</h1>
    <p>{len(species)} species &middot; <a href="{checklist_escaped}">View on eBird</a></p>
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
