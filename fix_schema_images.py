#!/usr/bin/env python3
"""
Scans all .html files in the current directory (recursively) for
Article/TechArticle/ScholarlyArticle JSON-LD blocks missing an "image"
field, and fills it in using that page's existing <meta property="og:image">
tag. Does NOT touch datePublished or author -- those need a real date/value,
not a guessed one, so they're only reported, not auto-fixed.

Usage:
    python fix_schema_images.py

Run from the repo root. Modifies files in place. Review with `git diff`
before committing.
"""
import re
import json
import glob

ARTICLE_TYPES = {"Article", "TechArticle", "ScholarlyArticle", "NewsArticle", "BlogPosting"}

files = glob.glob("**/*.html", recursive=True)

fixed_count = 0
still_missing = []

for path in files:
    with open(path, encoding="utf-8", errors="ignore") as f:
        html = f.read()

    og_image_match = re.search(r'<meta property="og:image" content="([^"]+)"', html)
    og_image = og_image_match.group(1) if og_image_match else None

    blocks = list(re.finditer(r'<script type="application/ld\+json">(.*?)</script>', html, re.S))
    if not blocks:
        continue

    changed = False
    new_html = html

    for m in blocks:
        raw = m.group(1)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue

        items = data if isinstance(data, list) else [data]
        block_changed = False

        for item in items:
            if not isinstance(item, dict):
                continue
            t = item.get("@type")
            types = t if isinstance(t, list) else [t]
            if not any(ty in ARTICLE_TYPES for ty in types):
                continue

            if "image" not in item:
                if og_image:
                    item["image"] = og_image
                    block_changed = True
                    changed = True
                else:
                    still_missing.append((path, "image", "no og:image found to copy from"))

            if "datePublished" not in item:
                still_missing.append((path, "datePublished", "needs a real date, not auto-fixed"))

            if "author" not in item:
                still_missing.append((path, "author", "needs a real value, not auto-fixed"))

        if block_changed:
            new_block = json.dumps(data, ensure_ascii=False, indent=2)
            new_html = new_html.replace(raw, new_block, 1)

    if changed:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_html)
        fixed_count += 1
        print(f"FIXED image: {path}")

print(f"\n{fixed_count} file(s) updated with 'image' field.")

if still_missing:
    print(f"\n{len(still_missing)} field(s) still need manual attention:")
    for path, field, reason in still_missing:
        print(f"  {path} :: missing '{field}' ({reason})")
