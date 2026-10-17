import requests, re, json

url = 'https://narto-drama.com?lang=es-ES'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

r = requests.get(url, headers=headers, timeout=10)
print('Status:', r.status_code)

# Find drama links /detail/watch/...
dramas = set(re.findall(r'/detail/watch/([^\"\'/?#]+)', r.text))
print(f"Found {len(dramas)} dramas on narto homepage:")
for slug in list(dramas)[:15]:
    print(" -", slug)
