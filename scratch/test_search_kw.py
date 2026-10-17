import urllib.request
import re

req = urllib.request.Request('https://www.reelshort.com/es/search?kw=amor', headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
try:
    html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
    print('Search kw length:', len(html))
    links = set(re.findall(r'/es/full-episodes/([a-zA-Z0-9_-]+)', html))
    print(f"Links found with kw=amor: {len(links)}")
    for l in list(links)[:10]:
        print(" ", l)
except Exception as e:
    print('Err:', e)
