import requests
import re

url = 'https://narto-drama.com/detail/watch/ecos-de-la-fatalidad/1?lang=es-ES'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://narto-drama.com/'
}
r = requests.get(url, headers=headers, timeout=10)
html = r.text

idx = html.find('vividshort.com')
if idx != -1:
    print("=== AROUND VIVIDSHORT ===")
    print(html[max(0, idx - 500): min(len(html), idx + 800)])

idx2 = html.find('sansekai')
if idx2 != -1:
    print("=== AROUND SANSEKAI ===")
    print(html[max(0, idx2 - 300): min(len(html), idx2 + 500)])
