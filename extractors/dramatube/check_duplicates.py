import json, os, sys

if sys.platform == 'win32':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except: pass

d = json.load(open('data/dramatube.json', encoding='utf-8'))
print(f"Total dramas in data/dramatube.json: {len(d)}")

posters = [x.get('poster') for x in d if x.get('poster')]
unique_posters = set(posters)
print(f"Unique posters count: {len(unique_posters)}")

# Check duplicates
poster_counts = {}
for x in d:
    p = x.get('poster')
    poster_counts[p] = poster_counts.get(p, 0) + 1

duplicates = {k: v for k, v in poster_counts.items() if v > 1}
print(f"Posters with duplicate usage: {len(duplicates)}")
if duplicates:
    print("Sample duplicate counts:", list(duplicates.items())[:5])

print("\nSample first 10 items:")
for i, x in enumerate(d[:10], 1):
    print(f"  {i}. {x.get('title')} -> {str(x.get('poster'))[:60]}...")
