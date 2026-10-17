import re
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('scratch/kurz_home_svelte.js', 'r', encoding='utf-8') as f:
    code = f.read()

items = {}
pattern = re.compile(r'([a-zA-Z0-9_$]+)\.([a-zA-Z0-9_]+)\s*=\s*(".*?"|\'.*?\'|\d+);')
for m in pattern.finditer(code):
    vname, prop, val = m.group(1), m.group(2), m.group(3).strip('"\'')
    if vname not in items:
        items[vname] = {}
    items[vname][prop] = int(val) if val.isdigit() else val

dramas = [v for v in items.values() if 'title' in v and 'href' in v]
print(f'Total dramas parsed from home: {len(dramas)}')

shelves = {}
for d in dramas:
    sh = d.get('shelf_name', 'General')
    shelves.setdefault(sh, []).append(d)

print(f'Total shelves: {len(shelves)}')
for sh, lst in shelves.items():
    print(f"Section [{sh}]: {len(lst)} dramas")

with open('scratch/kurz_parsed_home.json', 'w', encoding='utf-8') as f:
    json.dump({'shelves': shelves, 'dramas': dramas}, f, ensure_ascii=False, indent=2)

print('Saved scratch/kurz_parsed_home.json successfully!')
