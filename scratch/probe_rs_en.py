import requests
import json
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
r = requests.get('https://www.reelshort.com', headers={'User-Agent': UA}, timeout=10)

next_data = re.search(r'<script id="__NEXT_DATA__" type="application/json">([^<]+)</script>', r.text)
if next_data:
    d = json.loads(next_data.group(1))
    web_info = d['props']['pageProps']['fallback']['/api/ms/hall/webInfo']
    shelves = web_info['bookShelfList']
    print(f"Total shelves in ReelShort EN: {len(shelves)}")
    en_books = {}
    for sh in shelves:
        name = sh.get('name') or sh.get('title')
        b_list = sh.get('books') or []
        print(f"  Shelf: {name} -> {len(b_list)} books")
        for b in b_list:
            bid = b.get('book_id') or b.get('id')
            if bid:
                en_books[bid] = b
    print(f"Total unique books on ReelShort EN home: {len(en_books)}")
