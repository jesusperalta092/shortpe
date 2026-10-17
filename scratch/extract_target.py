import json
import re
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import sys
sys.stdout.reconfigure(encoding='utf-8')

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
HEADERS = {'User-Agent': UA, 'Referer': 'https://www.kurzdrama.com/'}

# 1. Load parsed home
with open('scratch/kurz_parsed_home.json', 'r', encoding='utf-8') as f:
    raw_home = json.load(f)

shelves_raw = raw_home['shelves']
all_raw_dramas = raw_home['dramas']

print(f"Total raw drama entries from home: {len(all_raw_dramas)}")
print(f"Total shelves: {len(shelves_raw)}")

def get_book_slug(href):
    t = href.split('/episodes/')[-1].strip('/')
    m = re.search(r'([a-f0-9]{24})', t)
    if not m:
        return None, None
    hex_id = m.group(1)
    prefix = t[:t.index(hex_id)]
    prefix = re.sub(r'^episode-\d+-', '', prefix, flags=re.I).rstrip('-')
    return hex_id, f"{prefix}-{hex_id}"

# Build unique dramas map, preserving shelf order
unique_dramas = {}
shelf_order = list(shelves_raw.keys())

for shelf_name, d_list in shelves_raw.items():
    for d in d_list:
        href = d.get('href', '')
        hex_id, book_slug = get_book_slug(href)
        if not hex_id or not book_slug:
            continue
        
        slug = f"dt-{book_slug}"
        if slug not in unique_dramas:
            unique_dramas[slug] = {
                'slug': slug,
                'title': d.get('title', '').strip(),
                'original_title': d.get('title', '').strip(),
                'bookId': hex_id,
                'book_slug': book_slug,
                'first_slug': href.split('/episodes/')[-1].strip('/'),
                'poster': d.get('image', ''),
                'shelf': shelf_name,
                'shelves': [shelf_name],
                'source': 'kurzdrama',
                'section': 'dramatube',
                'total_episodes': int(d.get('chapter_count', 0)) or 1,
                'collect_count': int(d.get('collect_count', 0)),
                'episodes': {}  # map ep_str -> {slug, m3u8}
            }
        else:
            if shelf_name not in unique_dramas[slug]['shelves']:
                unique_dramas[slug]['shelves'].append(shelf_name)

print(f"Total unique dramas across all shelves: {len(unique_dramas)}")

# 2. Function to scrape all episode slugs for a drama
def scrape_episodes_for_drama(item):
    book_slug = item['book_slug']
    url = f"https://www.reelshort.com/es/full-episodes/{book_slug}"
    eps = {}
    try:
        r = requests.get(url, headers={'User-Agent': UA}, timeout=12)
        if r.status_code != 200:
            return item['slug'], eps
        
        # Determine total pages
        pages = [1]
        for p in re.findall(r'/full-episodes/[^"\'\s>]+/(\d+)', r.text):
            pages.append(int(p))
        max_p = max(pages) if pages else 1
        
        def extract_eps_from_html(html):
            soup = BeautifulSoup(html, 'html.parser')
            for a in soup.find_all('a', href=True):
                h = a['href']
                if '/episodes/' in h:
                    ep_slug = h.split('/episodes/')[-1].strip('/')
                    num_m = re.search(r'episode-(\d+)', ep_slug, re.IGNORECASE)
                    num = int(num_m.group(1)) if num_m else 0
                    if num > 0:
                        ep_title = a.get_text(strip=True) or f"Episodio {num}"
                        if str(num) not in eps:
                            eps[str(num)] = {
                                'number': num,
                                'slug': ep_slug,
                                'title': ep_title,
                                'm3u8': ''
                            }
        
        extract_eps_from_html(r.text)
        
        for p in range(2, max_p + 1):
            rp = requests.get(f"{url}/{p}", headers={'User-Agent': UA}, timeout=12)
            if rp.status_code == 200:
                extract_eps_from_html(rp.text)
                
    except Exception as e:
        print(f"Error scraping episodes for {item['title']}: {e}")
        
    return item['slug'], eps

# Let's test scraping the target drama "Unida al Alfa y su Beta" first
target_slug = "dt-unida-al-alfa-y-su-beta-6a433648a0263ac457025610"
if target_slug in unique_dramas:
    _, target_eps = scrape_episodes_for_drama(unique_dramas[target_slug])
    unique_dramas[target_slug]['episodes'] = target_eps
    unique_dramas[target_slug]['total_episodes'] = len(target_eps)
    print(f"Target drama '{unique_dramas[target_slug]['title']}' extracted {len(target_eps)} episodes successfully!")
    
    # Also fetch m3u8 for Ep 1 of target drama
    ep1_slug = target_eps['1']['slug']
    r_ep1 = requests.get(f"https://www.kurzdrama.com/es/episodes/{ep1_slug}", headers=HEADERS, timeout=10)
    m = re.search(r'https?://v-mps\.crazymaplestudios\.com/[^\s"\'<>]+\.m3u8', r_ep1.text)
    if m:
        target_eps['1']['m3u8'] = m.group(0)
        print(f"Target ep 1 m3u8 stream confirmed: {m.group(0)}")
