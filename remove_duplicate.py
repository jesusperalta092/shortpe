import json
import os

target_slug = 'mi-profesor-es-mi-alfa-doblado'

# 1. catalog_full.json
if os.path.exists('catalog_full.json'):
    with open('catalog_full.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    before = len(data)
    data = [d for d in data if d.get('slug') != target_slug]
    after = len(data)
    with open('catalog_full.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f'catalog_full.json: {before} -> {after} (removed {before - after})')

# 2. _checkpoint.json (if present)
if os.path.exists('_checkpoint.json'):
    with open('_checkpoint.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    if isinstance(data, list):
        before = len(data)
        data = [d for d in data if d.get('slug') != target_slug]
        after = len(data)
        with open('_checkpoint.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f'_checkpoint.json: {before} -> {after} (removed {before - after})')
    elif isinstance(data, dict):
        if target_slug in data:
            del data[target_slug]
            with open('_checkpoint.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f'_checkpoint.json: removed key {target_slug}')

# 3. Any other json file
for fn in ['catalog.json', 'data/narto.json', 'data/netshort.json', 'catalog_freereels.json', 'data/dramatube.json', 'cukelis.json']:
    if os.path.exists(fn):
        with open(fn, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if isinstance(data, list):
            before = len(data)
            data = [d for d in data if d.get('slug') != target_slug]
            after = len(data)
            if before != after:
                with open(fn, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f'{fn}: removed {before - after} item(s)')
