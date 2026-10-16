import json
import re
import requests
import time
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(ROOT, 'data', 'dramatube.json')
SHELVES_PATH = os.path.join(ROOT, 'data', 'dramatube_shelves.json')

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
HEADERS = {'User-Agent': UA}

def scrape_episodes_for_item(item):
    slug = item['slug']
    title = item.get('title', '')
    bid = item.get('bookId', '')
    bslug = item.get('book_slug', '')
    
    # If already has episodes matching chapter count, skip
    existing_eps = item.get('episodes', {})
    expected = item.get('total_episodes', 0)
    if len(existing_eps) > 0 and len(existing_eps) >= expected:
        return slug, existing_eps, len(existing_eps)

    candidates = []
    if bslug: candidates.append(bslug)
    if bid: candidates.append(bid)
    
    eps = dict(existing_eps) # keep any existing ones
    session = requests.Session()
    
    for cand in candidates:
        url = f"https://www.reelshort.com/es/full-episodes/{cand}"
        for attempt in range(2):
            try:
                r = session.get(url, headers=HEADERS, timeout=12)
                if r.status_code != 200:
                    continue
                
                pages = [1]
                for p in re.findall(rf'/full-episodes/{re.escape(cand)}/(\d+)', r.text):
                    pages.append(int(p))
                for p in re.findall(r'/full-episodes/[^"\'\s>]+/(\d+)', r.text):
                    pages.append(int(p))
                max_page = max(pages) if pages else 1
                
                def parse_html(html):
                    soup = BeautifulSoup(html, 'html.parser')
                    for a in soup.find_all('a', href=True):
                        h = a['href']
                        if '/episodes/' in h:
                            ep_slug = h.split('/episodes/')[-1].strip('/')
                            m_num = re.search(r'episode-(\d+)', ep_slug, re.IGNORECASE)
                            num = int(m_num.group(1)) if m_num else 0
                            if num > 0 and str(num) not in eps:
                                t = a.get_text(strip=True) or f"Episodio {num}"
                                eps[str(num)] = {
                                    'number': num,
                                    'slug': ep_slug,
                                    'title': t,
                                    'm3u8': ''
                                }
                
                parse_html(r.text)
                
                for p in range(2, max_page + 1):
                    p_url = f"https://www.reelshort.com/es/full-episodes/{cand}/{p}"
                    pr = session.get(p_url, headers=HEADERS, timeout=12)
                    if pr.status_code == 200:
                        parse_html(pr.text)
                
                if len(eps) > 0:
                    break
            except Exception as e:
                time.sleep(1)
        if len(eps) > 0:
            break

    # If ReelShort had no eps, try first_slug on kurzdrama for ep 1
    if len(eps) == 0 and item.get('first_slug'):
        fs = item.get('first_slug')
        eps['1'] = {
            'number': 1,
            'slug': fs,
            'title': 'Episodio 1',
            'm3u8': ''
        }

    return slug, eps, len(eps)

def main():
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        dramas = json.load(f)

    print(f"Loaded {len(dramas)} dramas. Auditing episode counts...")
    need_scrape = [d for d in dramas if len(d.get('episodes', {})) < d.get('total_episodes', 1)]
    print(f"{len(need_scrape)} dramas need episode scraping.")

    completed = 0
    with ThreadPoolExecutor(max_workers=6) as ex:
        futures = {ex.submit(scrape_episodes_for_item, d): d for d in need_scrape}
        for fut in as_completed(futures):
            d = futures[fut]
            try:
                slug, eps, count = fut.result()
                d['episodes'] = eps
                if count > 0:
                    d['total_episodes'] = count
                completed += 1
                print(f"[{completed}/{len(need_scrape)}] {d['title']} -> {count} eps", flush=True)
            except Exception as e:
                print(f"Error on {d.get('title')}: {e}", flush=True)

    # Save data/dramatube.json
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(dramas, f, ensure_ascii=False, indent=2)
    print(f"\nSaved updated data to {DATA_PATH}")

    # Update shelves
    with open(SHELVES_PATH, 'r', encoding='utf-8') as f:
        sh_data = json.load(f)

    drama_map = {d['slug']: d for d in dramas}
    for sh in sh_data.get('shelves', []):
        for it in sh.get('items', []) + sh.get('all_items', []):
            s = it.get('slug')
            if s in drama_map:
                it['total_episodes'] = drama_map[s].get('total_episodes', it.get('total_episodes'))

    with open(SHELVES_PATH, 'w', encoding='utf-8') as f:
        json.dump(sh_data, f, ensure_ascii=False, indent=2)
    print(f"Saved updated shelves to {SHELVES_PATH}")

if __name__ == '__main__':
    main()
