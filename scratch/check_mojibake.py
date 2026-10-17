import json
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('data/dramatube.json', 'r', encoding='utf-8') as f:
    dramas = json.load(f)

bad_count = 0
for d in dramas:
    t = d.get('title', '')
    if any(c in t for c in ['Ã', 'Â', 'â', 'ð']):
        print("Bad title in dramatube.json:", t)
        bad_count += 1

print(f"Total bad titles in dramatube.json: {bad_count}")

with open('data/dramatube_shelves.json', 'r', encoding='utf-8') as f:
    sh_data = json.load(f)

bad_sh_count = 0
for sh in sh_data.get('shelves', []):
    for it in sh.get('items', []) + sh.get('all_items', []):
        t = it.get('title', '')
        if any(c in t for c in ['Ã', 'Â', 'â', 'ð']):
            print("Bad title in shelves:", t)
            bad_sh_count += 1
            break

print(f"Total bad titles in shelves: {bad_sh_count}")
