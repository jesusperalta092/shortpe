import requests
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
js_url = 'https://www.reelshort.com/_next/static/chunks/pages/search-d5f41a01b78d0dbb.js'
r = requests.get(js_url, headers={'User-Agent': UA}, timeout=10)

print(f"search script length: {len(r.text)}")
for m in set(re.findall(r'["\'](/api/[^"\']+)["\']', r.text)):
    print("  API match:", m)

# Search for /ms/ or fetch or axios
for m in set(re.findall(r'["\']([^"\']*(?:search|query|book)[^"\']*)["\']', r.text)):
    if '/' in m and len(m) < 60:
        print("  Pattern with slash:", m)
