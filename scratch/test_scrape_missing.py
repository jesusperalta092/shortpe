import requests
from bs4 import BeautifulSoup
import re
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

def scrape_drama_episodes(book_slug, book_id):
    # Try book_slug first, fallback to hex ID
    candidates = [book_slug, book_id]
    eps = {}
    
    for cand in candidates:
        if not cand: continue
        url = f"https://www.reelshort.com/es/full-episodes/{cand}"
        try:
            r = requests.get(url, headers={'User-Agent': UA}, timeout=10)
            if r.status_code != 200:
                continue
            
            # Find all pages
            pages = [1]
            for p in re.findall(rf'/full-episodes/{re.escape(cand)}/(\d+)', r.text):
                pages.append(int(p))
            for p in re.findall(r'/full-episodes/[^"\'\s>]+/(\d+)', r.text):
                pages.append(int(p))
            max_page = max(pages) if pages else 1
            
            def parse_page(html):
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
            
            parse_page(r.text)
            
            # Fetch remaining pages if any
            for p in range(2, max_page + 1):
                p_url = f"https://www.reelshort.com/es/full-episodes/{cand}/{p}"
                pr = requests.get(p_url, headers={'User-Agent': UA}, timeout=10)
                if pr.status_code == 200:
                    parse_page(pr.text)
            
            if len(eps) > 0:
                break
        except Exception as e:
            print(f"Error scraping {cand}: {e}")
            
    return eps

# Test on 3 dramas that were missing episodes
test_ids = [
    ('mi-jefe-multimillonario-no-me-deja-ir-6a7ae6e23bf7057327052251', '6a7ae6e23bf7057327052251'),
    ('me-enamore-de-un-granjero-y-papa-soltero-69def1b09533ee58430483c6', '69def1b09533ee58430483c6'),
    ('mi-dulce-novia-salvaje-6912a7d50f5968315e0b4328', '6912a7d50f5968315e0b4328')
]

for bs, bid in test_ids:
    eps = scrape_drama_episodes(bs, bid)
    print(f"Drama {bs[:30]}... (ID: {bid}) -> scraped {len(eps)} episodes!")
