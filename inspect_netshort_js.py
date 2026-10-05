import requests, re

url = 'https://netshort.com/episode/claimed-by-three-alphas-2105968477965524993'
r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).text

chunks = re.findall(r'src="(/_next/static/chunks/[^"]+)"', r)
print(f"Found {len(chunks)} JS chunks")

for c in chunks[:10]:
    js_url = 'https://netshort.com' + c
    js = requests.get(js_url, headers={'User-Agent': 'Mozilla/5.0'}).text
    # Search for api paths, fetch URLs, endpoints
    apis = re.findall(r'["\'](/api/[^"\']+|https?://[^"\']*(?:api|drama|episode|play|vod)[^"\']*)["\']', js)
    if apis:
        print(f"Chunk {c}:")
        for a in set(apis):
            if len(a) < 100:
                print(f"   -> {a}")
