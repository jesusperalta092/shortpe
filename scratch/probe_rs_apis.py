import requests
import json
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

# Let's inspect the JavaScript bundle of Reelshort to find all API routes
r = requests.get('https://www.reelshort.com/es', headers={'User-Agent': UA}, timeout=10)
js_files = re.findall(r'src=["\']([^"\']+\.js)["\']', r.text)
print(f"Found {len(js_files)} JS scripts on reelshort /es")

api_patterns = set()
for jf in js_files[:15]:
    if jf.startswith('/'):
        jf = 'https://www.reelshort.com' + jf
    try:
        rjs = requests.get(jf, headers={'User-Agent': UA}, timeout=6)
        matches = re.findall(r'["\'](/api/ms/[^"\']+)["\']', rjs.text)
        for m in matches:
            api_patterns.add(m)
    except: pass

print(f"Found {len(api_patterns)} API endpoints in ReelShort scripts:")
for ap in sorted(api_patterns):
    print("  ", ap)
