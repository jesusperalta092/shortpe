import requests
import json
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
r = requests.get('https://www.reelshort.com/es/search', headers={'User-Agent': UA}, timeout=10)

next_data = re.search(r'<script id="__NEXT_DATA__" type="application/json">([^<]+)</script>', r.text)
if next_data:
    d = json.loads(next_data.group(1))
    print("search page __NEXT_DATA__ keys:", list(d.keys()))
    print("pageProps:", d.get('props', {}).get('pageProps', {}))

# Also search for API endpoints in search page
scripts = re.findall(r'src=["\']([^"\']+\.js)["\']', r.text)
print("Search scripts:", len(scripts))
for s in scripts:
    if 'search' in s.lower():
        print("  Found search script:", s)
        try:
            js_url = 'https://www.reelshort.com' + s if s.startswith('/') else s
            js_r = requests.get(js_url, headers={'User-Agent': UA}, timeout=6)
            for m in set(re.findall(r'["\'](/api/[^"\']+)["\']', js_r.text)):
                print("    API route in search:", m)
        except Exception as e:
            print("    err:", e)
