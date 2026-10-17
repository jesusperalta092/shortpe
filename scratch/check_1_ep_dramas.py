import json
import requests
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

with open('data/dramatube.json', 'r', encoding='utf-8') as f:
    dramas = json.load(f)

sample_1_eps = [d for d in dramas if len(d.get('episodes', {})) == 1][:3]
for d in sample_1_eps:
    print(f"Title: {d.get('title')}, first_slug: {d.get('first_slug')}")
    # Inspect kurzdrama page for first_slug
    fs = d.get('first_slug')
    if fs:
        url = f"https://www.kurzdrama.com/es/episodes/{fs}"
        r = requests.get(url, headers={'User-Agent': UA, 'Referer': 'https://www.kurzdrama.com/'}, timeout=10)
        print(f"  Kurzdrama status: {r.status_code}")
        # Search for episode list or next episodes or svelte payload
        all_eps = set(re.findall(r'/es/episodes/([a-zA-Z0-9_\-%]+)', r.text))
        print(f"  Episodes referenced in kurzdrama page: {len(all_eps)}")
        for ep in list(all_eps)[:5]:
            print("   ", ep)
