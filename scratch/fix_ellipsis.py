import json

# Fix dramatube.json
with open('data/dramatube.json', 'r', encoding='utf-8') as f:
    dramas = json.load(f)

for d in dramas:
    if 'mentiras' in d.get('title', ''):
        d['title'] = d['title'].replace('â€¦', '…')
        d['original_title'] = d['title']

with open('data/dramatube.json', 'w', encoding='utf-8') as f:
    json.dump(dramas, f, ensure_ascii=False, indent=2)

# Fix dramatube_shelves.json
with open('data/dramatube_shelves.json', 'r', encoding='utf-8') as f:
    sh_data = json.load(f)

for sh in sh_data.get('shelves', []):
    for it in sh.get('items', []) + sh.get('all_items', []):
        if 'mentiras' in it.get('title', ''):
            it['title'] = it['title'].replace('â€¦', '…')

with open('data/dramatube_shelves.json', 'w', encoding='utf-8') as f:
    json.dump(sh_data, f, ensure_ascii=False, indent=2)

print("Fixed 'mentiras' ellipsis in data files.")
