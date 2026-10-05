import os, sys, json, requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

if sys.platform == 'win32':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except: pass

DATA_PATH = 'data/dramatube.json'
catalog = json.load(open(DATA_PATH, encoding='utf-8'))
print(f"Total catalog to validate: {len(catalog)}")

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

def validate_item(item):
    item['poster_local'] = ''
    slug = item.get('original_slug') or item.get('slug', '').replace('dt-', '')
    poster = item.get('poster', '').strip()

    # 1. Quick test current poster
    if poster and poster.startswith('http') and 'tiktokcdn' not in poster:
        try:
            r = requests.get(poster, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5, stream=True)
            if r.status_code == 200 and not r.headers.get('Content-Type', '').startswith('text/html'):
                return item
        except Exception:
            pass

    # 2. If broken or 404, fetch fresh og:image from dramaexpress
    try:
        page_url = f'https://dramaexpress.net/series/{slug}/episode-1'
        r = requests.get(page_url, headers=HEADERS, timeout=8)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            og = soup.find('meta', property='og:image')
            if og and og.get('content') and 'tiktokcdn' not in og['content']:
                cand = og['content'].strip()
                pr = requests.get(cand, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5, stream=True)
                if pr.status_code == 200 and not pr.headers.get('Content-Type', '').startswith('text/html'):
                    item['poster'] = cand
                    return item
    except Exception:
        pass

    return None

print("Validating all dramas...")
valid_items = []
with ThreadPoolExecutor(max_workers=12) as executor:
    futures = [executor.submit(validate_item, x) for x in catalog]
    for f in futures:
        res = f.result()
        if res:
            valid_items.append(res)

print(f"\nTotal Valid Dramas with 100% working live poster URLs: {len(valid_items)}")

# Deduplicate strictly
seen_posters = set()
seen_titles = set()
final_catalog = []

for x in valid_items:
    p = x['poster'].split('?')[0]
    t = x['title'].lower()
    if p not in seen_posters and t not in seen_titles:
        seen_posters.add(p)
        seen_titles.add(t)
        final_catalog.append(x)

print(f"Final clean & unique catalog size: {len(final_catalog)}")

with open(DATA_PATH, 'w', encoding='utf-8') as f:
    json.dump(final_catalog, f, ensure_ascii=False, indent=2)

print("Saved clean catalog to data/dramatube.json successfully!")
