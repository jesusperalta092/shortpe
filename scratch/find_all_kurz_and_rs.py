import requests
import json
import re
import xml.etree.ElementTree as ET
import sys
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
HEADERS = {'User-Agent': UA}

print("=== CHECKING REELSHORT ES HOMEPAGE ===")
r_rs = requests.get('https://www.reelshort.com/es', headers=HEADERS, timeout=12)
m = re.search(r'<script id="__NEXT_DATA__" type="application/json">([^<]+)</script>', r_rs.text)
rs_books = {}
if m:
    data = json.loads(m.group(1))
    web_info = data.get('props', {}).get('pageProps', {}).get('fallback', {}).get('/api/ms/hall/webInfo', {})
    shelves = web_info.get('bookShelfList', [])
    print(f"ReelShort ES shelves: {len(shelves)}")
    for sh in shelves:
        name = sh.get('name') or sh.get('title')
        books = sh.get('books') or []
        print(f"  Shelf: {name} -> {len(books)} books")
        for b in books:
            book_id = b.get('book_id')
            title = b.get('book_title')
            slug = b.get('book_slug') or b.get('app_page') or b.get('jump_param')
            if book_id:
                rs_books[str(book_id)] = {
                    'title': title,
                    'book_id': book_id,
                    'cover': b.get('cover_url') or b.get('book_pic') or b.get('pic'),
                    'slug': slug,
                    'shelf': name,
                    'total_episodes': b.get('chapter_count')
                }

print(f"Total unique books in ReelShort /es: {len(rs_books)}")

print("\n=== CHECKING KURZDRAMA ES HOMEPAGE ===")
with open('scratch/kurz_parsed_home.json', 'r', encoding='utf-8') as f:
    kurz_home = json.load(f)

kurz_dramas = {}
for sh_name, d_list in kurz_home['shelves'].items():
    for d in d_list:
        href = d.get('href', '')
        t = href.split('/episodes/')[-1].strip('/')
        m_id = re.search(r'([a-f0-9]{24})', t)
        if m_id:
            hex_id = m_id.group(1)
            kurz_dramas[hex_id] = {
                'title': d.get('title'),
                'href': href,
                'image': d.get('image'),
                'shelf': sh_name,
                'chapter_count': d.get('chapter_count')
            }
print(f"KurzDrama ES home unique hex IDs: {len(kurz_dramas)}")

print("\n=== CHECKING KURZDRAMA SITEMAP ===")
r_sm = requests.get('https://www.kurzdrama.com/sitemap.xml', headers=HEADERS, timeout=12)
root = ET.fromstring(r_sm.content)
sitemap_dramas = {}
for loc in root.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
    u = loc.text.strip()
    if '/es/episodes/' in u:
        m_id = re.search(r'([a-f0-9]{24})', u)
        if m_id:
            hex_id = m_id.group(1)
            sitemap_dramas[hex_id] = u
print(f"KurzDrama sitemap unique hex IDs: {len(sitemap_dramas)}")

# Combined kurz home + sitemap
all_kurz_ids = set(kurz_dramas.keys()).union(set(sitemap_dramas.keys()))
print(f"KurzDrama COMBINED unique hex IDs: {len(all_kurz_ids)}")

# In sitemap not in home
only_in_sitemap = set(sitemap_dramas.keys()) - set(kurz_dramas.keys())
print(f"Hex IDs ONLY in sitemap: {len(only_in_sitemap)}")

# Let's inspect some of them
print("\nSample dramas in sitemap but not on homepage:")
for hid in list(only_in_sitemap)[:5]:
    print(f"  ID: {hid} -> {sitemap_dramas[hid]}")
