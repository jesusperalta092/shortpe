import json
import requests
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('data/dramatube.json', 'r', encoding='utf-8') as f:
    dramas = json.load(f)

print(f"Total dramas in dramatube.json: {len(dramas)}")

no_episodes = []
with_episodes = []
mojibake_slugs = []

for d in dramas:
    slug = d.get('slug', '')
    eps = d.get('episodes', {})
    if any(c in slug for c in ['Ã', 'Â', 'â', 'ð', '%']):
        mojibake_slugs.append((slug, d.get('title')))
    
    if len(eps) == 0:
        no_episodes.append((slug, d.get('title'), d.get('book_slug'), d.get('bookId')))
    else:
        with_episodes.append((slug, d.get('title'), len(eps)))

print(f"Dramas with mojibake slugs: {len(mojibake_slugs)}")
print(f"Dramas WITHOUT episodes dictionary: {len(no_episodes)}")
print(f"Dramas WITH episodes dictionary: {len(with_episodes)}")

print("\nSample mojibake slugs:")
for s, t in mojibake_slugs[:5]:
    print(f"  {t} -> {s}")

print("\nSample dramas WITHOUT episodes:")
for s, t, bs, bid in no_episodes[:5]:
    print(f"  {t} (ID: {bid}) -> book_slug: {bs}")
