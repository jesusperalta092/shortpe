import requests
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

routes = [
    '/es/explore',
    '/es/all',
    '/es/library',
    '/es/search',
    '/es/genres',
    '/es/tags',
    '/es/category',
    '/es/rank',
    '/es/popular',
    '/es/vip',
    '/es/browse'
]

for r_path in routes:
    url = f"https://www.reelshort.com{r_path}"
    try:
        res = requests.get(url, headers={'User-Agent': UA}, timeout=6)
        print(f"{r_path} -> {res.status_code}, len: {len(res.text)}")
        if res.status_code == 200:
            books = set(re.findall(r'href=["\'](/es/(?:full-episodes|episodes)/[^"\']+)["\']', res.text))
            print(f"   books found: {len(books)}")
    except Exception as e:
        print(f"{r_path} -> error: {e}")
