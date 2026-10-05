import requests, re, json, os

url = 'https://dramaexpress.net/series/30-day-bride/episode-1'
r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
print(f"Status: {r.status_code}")

# Let's search all image candidates in the HTML
matches = re.findall(r'(https?:[\\/]+[^"\'\s>]+\.(?:jpg|jpeg|png|webp)[^"\'\s>]*)', r.text)
for m in matches:
    clean = m.replace(r'\/', '/')
    print("Found candidate image:", clean)
