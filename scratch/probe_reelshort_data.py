import requests
import json
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
r = requests.get('https://www.reelshort.com/es', headers={'User-Agent': UA}, timeout=10)

next_data = re.search(r'<script id="__NEXT_DATA__" type="application/json">([^<]+)</script>', r.text)
if next_data:
    d = json.loads(next_data.group(1))
    props = d.get('props', {}).get('pageProps', {})
    fallback = props.get('fallback', {})
    web_info = fallback.get('/api/ms/hall/webInfo')
    print("Type of web_info:", type(web_info))
    if isinstance(web_info, dict):
        print("web_info keys:", list(web_info.keys()))
        data = web_info.get('data', web_info)
        print("data keys:", list(data.keys()) if isinstance(data, dict) else type(data))
        if isinstance(data, dict):
            for k in data:
                v = data[k]
                if isinstance(v, list):
                    print(f"  data['{k}'] len: {len(v)}")
                    if v and isinstance(v[0], dict):
                        print(f"    sample item keys: {list(v[0].keys())[:8]}")
                        # If shelves or books
                        if 'shelf_name' in v[0] or 'name' in v[0]:
                            for sh in v:
                                name = sh.get('shelf_name') or sh.get('name')
                                books = sh.get('book_list') or sh.get('books') or sh.get('items') or []
                                print(f"      Shelf: '{name}' -> {len(books)} books")
