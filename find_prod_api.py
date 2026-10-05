import requests, re

url = 'https://netshort.com/episode/claimed-by-three-alphas-2105968477965524993'
r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).text
chunks = re.findall(r'src="(/_next/static/chunks/[^"]+)"', r)

for c in chunks:
    js_url = 'https://netshort.com' + c
    js = requests.get(js_url, headers={'User-Agent': 'Mozilla/5.0'}).text
    matches = re.findall(r'["\'](/prod-web-api/[^"\']+)["\']', js)
    if matches:
        print(f"Chunk {c} contains prod-web-api paths:")
        for m in set(matches):
            print("  ", m)
