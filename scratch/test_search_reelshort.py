import urllib.request
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
req = urllib.request.Request('https://www.reelshort.com/es/search', headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
try:
    html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
    print('Search page length:', len(html))
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">([^<]+)</script>', html)
    if m:
        data = json.loads(m.group(1))
        fallback = data.get('props', {}).get('pageProps', {}).get('fallback', {})
        print('Fallback keys:', list(fallback.keys()))
        for k, v in fallback.items():
            print(f"Key: {k}")
            if isinstance(v, dict):
                print("  dict keys:", list(v.keys()))
                if 'data' in v:
                    d = v['data']
                    if isinstance(d, list):
                        print(f"  data list len: {len(d)}")
                        for item in d[:5]:
                            print("   ", item)
                    elif isinstance(d, dict):
                        print("  data dict keys:", list(d.keys()))
except Exception as e:
    print('Err:', e)
