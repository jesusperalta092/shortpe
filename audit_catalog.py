import json
import os
import requests

with open('data/dramatube.json', 'r', encoding='utf-8') as f:
    dramas = json.load(f)

print(f"Total dramas in dramatube.json: {len(dramas)}")

# 1. Check duplicate titles / slugs
slug_counts = {}
title_counts = {}
for d in dramas:
    s = d.get('slug')
    t = d.get('title')
    slug_counts[s] = slug_counts.get(s, 0) + 1
    title_counts[t] = title_counts.get(t, 0) + 1

dup_slugs = {k: v for k, v in slug_counts.items() if v > 1}
dup_titles = {k: v for k, v in title_counts.items() if v > 1}

print(f"\n1. DUPLICATE AUDIT:")
print(f"Duplicate Slugs: {len(dup_slugs)} -> sample: {list(dup_slugs.items())[:5]}")
print(f"Duplicate Titles: {len(dup_titles)} -> sample: {list(dup_titles.items())[:5]}")

# 2. Check broken / missing posters
missing_posters = [d for d in dramas if not d.get('poster') and not d.get('poster_local')]
print(f"\n2. POSTER AUDIT:")
print(f"Dramas with completely missing poster: {len(missing_posters)}")

# Sample check 10 posters for status code
sample_posters = [d.get('poster') for d in dramas if d.get('poster')][:15]
broken_posters = 0
for p in sample_posters:
    try:
        r = requests.head(p, headers={'User-Agent': 'Mozilla/5.0'}, timeout=4)
        if r.status_code >= 400:
            broken_posters += 1
            print(f"  Broken poster ({r.status_code}): {p}")
    except Exception as e:
        broken_posters += 1
        print(f"  Broken poster error: {p} -> {e}")

print(f"Sample broken posters: {broken_posters}/{len(sample_posters)}")
