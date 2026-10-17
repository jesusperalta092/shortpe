import json
with open('data/dramatube.json', 'r', encoding='utf-8') as f:
    dt = json.load(f)
print('dramatube.json total dramas:', len(dt))

with open('data/dramatube_shelves.json', 'r', encoding='utf-8') as f:
    sh = json.load(f)
shelves = sh.get('shelves', [])
print('dramatube_shelves.json total shelves:', len(shelves))
for s in shelves:
    print(f"  {s.get('name')}: items={len(s.get('items', []))}, all_items={len(s.get('all_items', [])) if 'all_items' in s else 'N/A'}")

