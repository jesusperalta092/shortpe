import json
import re
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

shelves = {}
for d in dramas:
    sh = d.get('shelf_name', 'General')
    shelves.setdefault(sh, []).append(d)

print(f"Total drama cards found on homepage: {len(dramas)}")
print(f"Total unique shelves: {len(shelves)}\n")

total_unique_dramas = {}
for sh, lst in shelves.items():
    print(f"Shelf: '{sh}' -> {len(lst)} titles")
    for d in lst:
        slug = d.get('href', '').split('/episodes/')[-1].strip('/')
        if slug not in total_unique_dramas:
            total_unique_dramas[slug] = d

print(f"\nTotal UNIQUE dramas across all shelves: {len(total_unique_dramas)}")
total_eps = sum(int(d.get('chapter_count', 0)) for d in total_unique_dramas.values())
print(f"Total episodes across all unique dramas: {total_eps}")

# Also check if kurzdrama has a sitemap or list page (like /es/all or sitemap.xml)
