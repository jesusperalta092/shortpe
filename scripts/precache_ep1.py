import json
import requests
import re
from concurrent.futures import ThreadPoolExecutor
import time
import sys
sys.stdout.reconfigure(encoding='utf-8')

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
HEADERS = {'User-Agent': UA, 'Referer': 'https://www.kurzdrama.com/'}

with open('data/dramatube.json', 'r', encoding='utf-8') as f:
    dramas = json.load(f)

print(f"Pre-caching ep 1 streams for {len(dramas)} dramas...")
t0 = time.time()

def cache_ep1(d):
    eps = d.get('episodes', {})
    ep1 = eps.get('1')
    if not ep1 or ep1.get('m3u8'):
        return
    slug = ep1.get('slug') or d.get('first_slug')
    if not slug:
        return
    try:
        r = requests.get(f"https://www.kurzdrama.com/es/episodes/{slug}", headers=HEADERS, timeout=8)
        m = re.search(r'https?://v-mps\.crazymaplestudios\.com/[^\s"\'<>]+\.m3u8', r.text)
        if m:
            ep1['m3u8'] = m.group(0)
    except: pass

with ThreadPoolExecutor(max_workers=15) as executor:
    list(executor.map(cache_ep1, dramas))

cached_count = sum(1 for d in dramas if d.get('episodes', {}).get('1', {}).get('m3u8'))
print(f"Pre-cached ep 1 for {cached_count}/{len(dramas)} dramas in {time.time()-t0:.2f}s!")

with open('data/dramatube.json', 'w', encoding='utf-8') as f:
    json.dump(dramas, f, ensure_ascii=False, indent=2)

print("Saved updated data/dramatube.json")
