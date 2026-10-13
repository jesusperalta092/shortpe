import json, sys

sys.stdout.reconfigure(encoding='utf-8')
from classify_hotdramas import spanish_list

print(f"Checking {len(spanish_list)} Spanish HotDramas:")
total_eps = 0
for i, d in enumerate(spanish_list):
    eps = d.get('episodes', {})
    total_eps += len(eps)
    print(f"{i+1:2d}. {d.get('title')} | slug: {d.get('slug')} | episodes: {len(eps)}")

print(f"Total episodes across 31 Spanish dramas: {total_eps}")
