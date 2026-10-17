import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('data/dramatube.json', 'r', encoding='utf-8') as f:
    dramas = json.load(f)

print(f"Total dramas in dramatube.json: {len(dramas)}")

# Check titles
for i, d in enumerate(dramas[:15]):
    print(f"[{i+1}] {d.get('title')} | Shelf: {d.get('shelf')} | Eps: {d.get('total_episodes')}")
