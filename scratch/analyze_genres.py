import json, os
from collections import Counter

# Test loading from server API or files
import urllib.request
r = urllib.request.urlopen('http://127.0.0.1:8090/api/catalog')
cat = json.loads(r.read())
print('Total catalog:', len(cat))

drama_items = [d for d in cat if d.get('section') == 'drama']
shorts_items = [d for d in cat if d.get('section') == 'dramashorts']

print('\nDRAMAS count:', len(drama_items))
drama_genres = Counter(g for d in drama_items for g in d.get('genres', []))
print('Top 25 genres in Dramas:')
for g, c in drama_genres.most_common(25):
    print(f"  - {g}: {c}")

print('\nDRAMASHORTS count:', len(shorts_items))
shorts_genres = Counter(g for d in shorts_items for g in d.get('genres', []))
print('Top 25 genres in DramaShorts:')
for g, c in shorts_genres.most_common(25):
    print(f"  - {g}: {c}")
