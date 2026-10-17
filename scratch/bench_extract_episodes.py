import json
import requests
import re
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import time
import sys
sys.stdout.reconfigure(encoding='utf-8')

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

with open('scratch/kurz_parsed_home.json', 'r', encoding='utf-8') as f:
    home_data = json.load(f)

dramas = home_data['dramas']
print(f"Loaded {len(dramas)} dramas from home_parsed.")

def get_book_slug(href):
    # e.g. /es/episodes/episode-1-unida-al-alfa-y-su-beta-6a433648a0263ac457025610-2az8aku8d1
    t = href.split('/episodes/')[-1].strip('/')
    m = re.search(r'([a-f0-9]{24})', t)
    if not m:
        return None
    hex_id = m.group(1)
    prefix = t[:t.index(hex_id)]
    prefix = re.sub(r'^episode-\d+-', '', prefix, flags=re.I).rstrip('-')
    return f"{prefix}-{hex_id}"

# Test for first 5 dramas
sample_dramas = dramas[:5]
t0 = time.time()

def fetch_drama_episodes(d):
    bslug = get_book_slug(d.get('href', ''))
    if not bslug:
        return d.get('title'), 0
    url = f"https://www.reelshort.com/es/full-episodes/{bslug}"
    try:
        r = requests.get(url, headers={'User-Agent': UA}, timeout=10)
        if r.status_code != 200:
            return d.get('title'), 0
        pages = [1]
        for p in re.findall(r'/full-episodes/[^"\'\s>]+/(\d+)', r.text):
            pages.append(int(p))
        max_p = max(pages) if pages else 1
        
        slugs = set()
        soup = BeautifulSoup(r.text, 'html.parser')
        for a in soup.find_all('a', href=True):
            if '/episodes/' in a['href']:
                slugs.add(a['href'].split('/episodes/')[-1].strip('/'))
        
        for p in range(2, max_p + 1):
            rp = requests.get(f"{url}/{p}", headers={'User-Agent': UA}, timeout=10)
            if rp.status_code == 200:
                soup_p = BeautifulSoup(rp.text, 'html.parser')
                for a in soup_p.find_all('a', href=True):
                    if '/episodes/' in a['href']:
                        slugs.add(a['href'].split('/episodes/')[-1].strip('/'))
        return d.get('title'), len(slugs)
    except Exception as e:
        return d.get('title'), -1

with ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(fetch_drama_episodes, sample_dramas))

print(f"Scraped {len(results)} sample dramas in {time.time()-t0:.2f}s:")
for title, count in results:
    print(f"  - {title}: {count} episodes")
