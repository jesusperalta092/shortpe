import json
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('data/dramatube.json', 'r', encoding='utf-8') as f:
    dramas = json.load(f)

for d in dramas:
    if 'Ã' in d.get('slug', '') or 'â' in d.get('slug', ''):
        print("Bad slug in dramatube:", d.get('slug'))

with open('data/dramatube_shelves.json', 'r', encoding='utf-8') as f:
    sh_data = json.load(f)

for sh in sh_data.get('shelves', []):
    for it in sh.get('items', []) + sh.get('all_items', []):
        if 'Ã' in it.get('slug', '') or 'â' in it.get('slug', ''):
            print("Bad slug in shelf item:", it.get('slug'))
            break
