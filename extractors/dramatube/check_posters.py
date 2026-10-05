import json, requests

d = json.load(open('data/dramatube.json', encoding='utf-8'))
print(f"Total dramas in dramatube: {len(d)}")

broken = []
valid = []
for i, x in enumerate(d):
    title = x.get('title')
    poster = x.get('poster')
    if not poster:
        broken.append((title, 'EMPTY POSTER', x.get('slug')))
        continue
    try:
        r = requests.head(poster, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
        if r.status_code != 200:
            broken.append((title, f"HTTP {r.status_code} on {poster}", x.get('slug')))
        else:
            valid.append((title, poster))
    except Exception as e:
        broken.append((title, f"Error: {e} on {poster}", x.get('slug')))

print(f"\nTotal Valid Posters: {len(valid)}")
print(f"Total Broken Posters: {len(broken)}")
print("\nFirst 15 Broken Posters:")
for b in broken[:15]:
    print(b)
