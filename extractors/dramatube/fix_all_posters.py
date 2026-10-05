import os, sys, json, re, requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

if sys.platform == 'win32':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except: pass

DATA_PATH = 'data/dramatube.json'
if not os.path.exists(DATA_PATH):
    print("data/dramatube.json does not exist")
    sys.exit(1)

catalog = json.load(open(DATA_PATH, encoding='utf-8'))
print(f"Loaded {len(catalog)} dramas from {DATA_PATH}")

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

PREFERRED_CDNS = [
    'dramaboxdb.com', 'goodshort.com', 'shorttv.live', 'mydramawave.com',
    'stardusttv.cc', 'farsunpteltd.com', 'crazymaplestudios.com', 'vigoo', 'alphashort'
]

def extract_best_poster(html_text, soup):
    candidates = re.findall(r'(https?:[\\/]+[^"\'\s>]+\.(?:jpg|jpeg|png|webp)[^"\'\s>]*)', html_text)
    cleaned = [c.replace(r'\/', '/').replace('\\', '') for c in candidates]
    
    # 1. Prefer stable CDN images
    for c in cleaned:
        for cdn in PREFERRED_CDNS:
            if cdn in c:
                return c.split('&amp;')[0]
                
    # 2. Cover / Poster regex
    pm = re.search(r'cover[\\"]*:\s*[\\"]*(https?:[\\/]+[^"\\\s]+)[\\"]*', html_text) or re.search(r'poster[\\"]*:\s*[\\"]*(https?:[\\/]+[^"\\\s]+)[\\"]*', html_text)
    if pm:
        p = pm.group(1).replace(r'\/', '/').replace('\\', '')
        if 'tiktokcdn' not in p:
            return p

    # 3. OG image
    og = soup.find('meta', property='og:image')
    if og and og.get('content') and 'tiktokcdn' not in og['content']:
        return og['content']

    # 4. Any other non-tiktok image
    for c in cleaned:
        if 'tiktokcdn' not in c and ('cover' in c or 'playlet' in c or 'chapter' in c or 'videobook' in c):
            return c.split('&amp;')[0]

    return cleaned[0] if cleaned else ''

def fix_item(item):
    slug = item.get('original_slug') or item.get('slug','').replace('dt-','')
    curr_poster = item.get('poster','')
    # If poster is missing, tiktokcdn, or broken
    needs_fix = not curr_poster or 'tiktokcdn' in curr_poster
    if not needs_fix:
        return item, False

    try:
        url = f'https://dramaexpress.net/series/{slug}/episode-1'
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            best = extract_best_poster(r.text, soup)
            if best:
                item['poster'] = best
                return item, True
    except Exception as e:
        pass
    return item, False

print("Fixing broken/tiktokcdn posters across catalog...")
fixed_count = 0
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(fix_item, x) for x in catalog]
    fixed_catalog = []
    for f in futures:
        item, was_fixed = f.result()
        fixed_catalog.append(item)
        if was_fixed:
            fixed_count += 1

print(f"Fixed {fixed_count} posters!")
with open(DATA_PATH, 'w', encoding='utf-8') as f:
    json.dump(fixed_catalog, f, ensure_ascii=False, indent=2)

print("Saved updated catalog to data/dramatube.json")
