import re
import json

with open('dramas-es-0.xml', 'r', encoding='utf-8') as f:
    text = f.read()

urls = re.findall(r'<loc>(.*?)</loc>', text)
print(f"Total Spanish URLs in sitemap: {len(urls)}")

dramas_info = []
for u in urls:
    m = re.search(r'/es/drama/([^/]+)', u)
    if m:
        slug = m.group(1)
        # title formatting
        raw = slug.replace('-', ' ')
        # fix common words
        dramas_info.append({
            'slug': slug,
            'url': u
        })

print(f"Parsed {len(dramas_info)} Spanish dramas.")
print("\nFirst 30 Spanish titles from Suikora:")
for i, d in enumerate(dramas_info[:30], 1):
    print(f"{i:2d}. {d['slug']}")
