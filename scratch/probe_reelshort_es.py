import requests
import re
from bs4 import BeautifulSoup
import sys
sys.stdout.reconfigure(encoding='utf-8')

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

r = requests.get('https://www.reelshort.com/es', headers={'User-Agent': UA}, timeout=10)
print("Reelshort /es status:", r.status_code, "len:", len(r.text))

# Search for /es/full-episodes/ or /es/episodes/ or /full-episodes/
matches = set(re.findall(r'href=["\'](/es/(?:full-episodes|episodes)/[^"\']+)["\']', r.text))
print("Unique drama links on reelshort /es homepage:", len(matches))
for m in sorted(matches)[:15]:
    print("  ", m)

# Also let's check next-data or state
next_data = re.search(r'<script id="__NEXT_DATA__" type="application/json">([^<]+)</script>', r.text)
if next_data:
    print("Found __NEXT_DATA__ in reelshort!")
    import json
    d = json.loads(next_data.group(1))
    print("Keys in next_data:", list(d.keys()))
    props = d.get('props', {}).get('pageProps', {})
    print("pageProps keys:", list(props.keys()))
    # Check if there are shelves/books
    for k in props:
        val = props[k]
        if isinstance(val, list):
            print(f"Prop '{k}' is list of len {len(val)}")
        elif isinstance(val, dict):
            print(f"Prop '{k}' is dict with keys: {list(val.keys())[:5]}")
