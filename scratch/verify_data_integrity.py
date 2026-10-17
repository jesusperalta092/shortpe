import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
with open('data/dramatube_banners.json', 'r', encoding='utf-8') as f:
    banners = json.load(f)
print("Banners available:", len(banners))

with open('data/dramatube_shelves.json', 'r', encoding='utf-8') as f:
    shelves = json.load(f)['shelves']
print("Shelves available:", len(shelves))
for sh in shelves:
    items = sh.get('items', [])
    all_items = sh.get('all_items', [])
    print(f"  {sh['name']}: {len(items)} items in carousel, {len(all_items)} total")
