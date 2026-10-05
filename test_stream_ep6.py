import requests
import re
import json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
r = requests.get('https://esdramia.com/dramas/un-beso-de-navidad-de-mi-rival/6', headers=headers, timeout=10)
print('Page /6 status:', r.status_code)
html = r.text

for m in re.finditer(r'\\"hash\\":\\"([0-9a-f]{32})\\"', html):
    h = m.group(1)
    sr = requests.get('https://esdramia.com/api/stream/' + h, headers=headers, timeout=10)
    print(f'Hash {h} -> status {sr.status_code}, body: {sr.text[:100]}')
