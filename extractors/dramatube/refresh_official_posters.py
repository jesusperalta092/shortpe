import os, sys, json, requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

if sys.platform == 'win32':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except: pass

DATA_PATH = 'data/dramatube.json'
catalog = json.load(open(DATA_PATH, encoding='utf-8'))
print(f"Loaded {len(catalog)} dramas from {DATA_PATH}")

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

def verify_and_fix_drama(item):
    # 1. Clear any local poster (strictly URL links only)
    item['poster_local'] = ''
    
    slug = item.get('original_slug') or item.get('slug', '').replace('dt-', '')
    poster = item.get('poster', '')
    
    # Check if current poster works
    poster_ok = False
    if poster and poster.startswith('http') and 'tiktokcdn' not in poster:
        try:
            r = requests.get(poster, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5, stream=True)
            if r.status_code == 200 and not r.headers.get('Content-Type','').startswith('text/html'):
                poster_ok = True
        except Exception:
            pass

    # If poster is broken or invalid, fetch fresh og:image from dramaexpress
    if not poster_ok:
        try:
            page_url = f'https://dramaexpress.net/series/{slug}/episode-1'
            r = requests.get(page_url, headers=HEADERS, timeout=8)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                og = soup.find('meta', property='og:image')
                if og and og.get('content') and 'tiktokcdn' not in og['content']:
                    cand = og['content']
                    pr = requests.get(cand, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5, stream=True)
                    if pr.status_code == 200 and not pr.headers.get('Content-Type','').startswith('text/html'):
                        item['poster'] = cand
                        poster_ok = True
        except Exception:
            pass

    # Check episode 1 stream validity
    eps = item.get('episodes', {})
    ep1 = eps.get('1', '')
    stream_ok = False
    if ep1 and 'tiktokcdn' not in ep1 and 'goodbos' not in ep1:
        try:
            sr = requests.get(ep1, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
            if sr.status_code == 200 and len(sr.content) > 50:
                stream_ok = True
        except Exception:
            pass

    if poster_ok and stream_ok:
        return item
    return None

print("Verifying and refreshing all official poster URLs across catalog...")
verified_catalog = []
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(verify_and_fix_drama, x) for x in catalog]
    for f in futures:
        res = f.result()
        if res:
            verified_catalog.append(res)

print(f"\nFinal 100% verified dramas with working official poster URLs: {len(verified_catalog)}")

# Deduplicate strictly by poster and title
final_list = []
seen_posters = set()
seen_titles = set()
for item in verified_catalog:
    p = item['poster'].split('?')[0]
    t = item['title'].lower()
    if p not in seen_posters and t not in seen_titles:
        seen_posters.add(p)
        seen_titles.add(t)
        final_list.append(item)

print(f"Final deduplicated catalog size: {len(final_list)}")

with open(DATA_PATH, 'w', encoding='utf-8') as f:
    json.dump(final_list, f, ensure_ascii=False, indent=2)

print(f"Saved {len(final_list)} dramas to {DATA_PATH}!")
