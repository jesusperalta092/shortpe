import json
import os

with open('data/dramatube.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)

print(f"Loaded {len(catalog)} dramas from data/dramatube.json")

fixed_count = 0
for d in catalog:
    eps = d.get('episodes', {})
    subs = d.get('subtitles', {})
    
    if not eps:
        continue
        
    # Sort existing keys by numeric value
    sorted_ep_keys = sorted(eps.keys(), key=lambda x: int(x) if x.isdigit() else 999999)
    
    new_eps = {}
    new_subs = {}
    
    for i, old_key in enumerate(sorted_ep_keys, start=1):
        new_key = str(i)
        new_eps[new_key] = eps[old_key]
        if subs and old_key in subs:
            new_subs[new_key] = subs[old_key]
            
    d['episodes'] = new_eps
    d['subtitles'] = new_subs
    d['total_episodes'] = len(new_eps)
    fixed_count += 1

with open('data/dramatube.json', 'w', encoding='utf-8') as f:
    json.dump(catalog, f, ensure_ascii=False, indent=2)

print(f"Successfully re-indexed {fixed_count} dramas to sequential keys 1..N in data/dramatube.json!")
