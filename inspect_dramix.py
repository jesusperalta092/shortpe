import requests
import json
import re

url = 'https://dramix.tv/es/drama/aventura-prohibida-con-el-papa-de-mi-mejor-amiga-doblado'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
    'Referer': 'https://dramix.tv/'
}

r = requests.get(url, headers=headers)
html = r.text

print(f"Status: {r.status_code}, Length: {len(html)}")

# Buscar __NEXT_DATA__ o scripts JSON
m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
if m:
    data = json.loads(m.group(1))
    print("Found __NEXT_DATA__!")
    with open('_dramix_full.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    page_props = data.get('props', {}).get('pageProps', {})
    print("pageProps keys:", list(page_props.keys()))
else:
    print("No __NEXT_DATA__ found. Scanning all script tags...")
    scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
    for i, s in enumerate(scripts):
        if len(s.strip()) > 20:
            print(f"Script {i} ({len(s)} chars): {s[:150]}...")
            if 'self.__next_f.push' in s:
                # Next.js App Router streaming RSC payload
                print("Found App Router payload in script", i)
