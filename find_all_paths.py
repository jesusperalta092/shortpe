import requests, re

url = 'https://netshort.com/episode/claimed-by-three-alphas-2105968477965524993'
r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).text
chunks = re.findall(r'src="(/_next/static/chunks/[^"]+)"', r)

for c in chunks:
    js = requests.get('https://netshort.com' + c, headers={'User-Agent': 'Mozilla/5.0'}).text
    paths = re.findall(r'["\'](/[a-zA-Z0-9_\-]+/[a-zA-Z0-9_\-]+(?:/[a-zA-Z0-9_\-]+)*)["\']', js)
    valid = [p for p in set(paths) if any(k in p for k in ['drama', 'episode', 'play', 'user', 'video', 'watch', 'order', 'unlock', 'coin', 'list', 'detail'])]
    if valid:
        print(f"Chunk {c}:")
        for p in valid:
            print("  ", p)
