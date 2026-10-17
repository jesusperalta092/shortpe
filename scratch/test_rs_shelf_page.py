import requests
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
headers = {
    'User-Agent': UA,
    'Referer': 'https://www.reelshort.com/es',
    'Accept': 'application/json, text/plain, */*',
    'content-type': 'application/json'
}

# In probe_rs_shelves, let's see what bs_id each shelf has
r = requests.get('https://www.reelshort.com/es', headers={'User-Agent': UA}, timeout=10)
import re
next_data = re.search(r'<script id="__NEXT_DATA__" type="application/json">([^<]+)</script>', r.text)
d = json.loads(next_data.group(1))
web_info = d['props']['pageProps']['fallback']['/api/ms/hall/webInfo']

shelves = web_info['bookShelfList']
for sh in shelves:
    bs_id = sh.get('bs_id')
    name = sh.get('name') or sh.get('title')
    books = sh.get('books') or []
    print(f"Shelf bs_id: {bs_id}, name: {name}, current books: {len(books)}")
    
    # Try calling webBookShelfPage for this shelf
    if bs_id:
        url = f"https://www.reelshort.com/api/ms/hall/webBookShelfPage?bs_id={bs_id}&page=1&page_size=30&locale=es"
        try:
            res = requests.get(url, headers=headers, timeout=6)
            print(f"   webBookShelfPage GET -> {res.status_code}, len: {len(res.text)}")
            if res.status_code == 200:
                print("   Snippet:", res.text[:200])
        except Exception as e:
            print("   error:", e)
        # Try POST as well
        try:
            res_p = requests.post("https://www.reelshort.com/api/ms/hall/webBookShelfPage", 
                                  json={"bs_id": bs_id, "page": 1, "page_size": 30, "locale": "es"}, 
                                  headers=headers, timeout=6)
            print(f"   webBookShelfPage POST -> {res_p.status_code}, len: {len(res_p.text)}")
            if res_p.status_code == 200:
                print("   POST snippet:", res_p.text[:200])
        except Exception as e:
            print("   post error:", e)
        break
