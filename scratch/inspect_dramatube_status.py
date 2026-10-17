import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('data/dramatube.json', 'r', encoding='utf-8') as f:
    dramas = json.load(f)

print(f"Total dramas in dramatube.json: {len(dramas)}")

# Count how many have episodes
with_eps = sum(1 for d in dramas if len(d.get('episodes', {})) > 0)
total_eps = sum(len(d.get('episodes', {})) for d in dramas)
print(f"Dramas with episodes: {with_eps} / {len(dramas)}, Total episodes: {total_eps}")

with open('data/dramatube_shelves.json', 'r', encoding='utf-8') as f:
    sh_data = json.load(f)

shelves = sh_data.get('shelves', [])
print(f"Total shelves: {len(shelves)}")
for sh in shelves:
    print(f"  Shelf: '{sh['name']}' -> items: {len(sh.get('items', []))}, all_items: {len(sh.get('all_items', []))}")
