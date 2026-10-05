import json, os, sys, requests

if sys.platform == 'win32':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except: pass

DATA_PATH = 'data/dramatube.json'
d = json.load(open(DATA_PATH, encoding='utf-8'))
print(f"Original count: {len(d)}")

# Known generic/sidebar repeat URLs to eliminate
FORBIDDEN_POSTERS = [
    'https://acf.goodshort.com/videobook/202609/cover-Os4BRoMS9Y.jpg',
    'https://zshipubcf.farsunpteltd.com/playlet/1790247319_Gan2hDNR8e.jpg',
    'https://hwztchapter.dramaboxdb.com/data/cppartner/4x2/42x0/420x0/42000029031/42000029031.jpg'
]

cleaned = []
seen_posters = set()
seen_titles = set()

for item in d:
    title = item.get('title', '').strip()
    poster = item.get('poster', '').strip()
    slug = item.get('slug', '')
    eps = item.get('episodes', {})

    if not poster or not title or not eps:
        continue

    # Filter out forbidden/sidebar repeat posters
    is_forbidden = False
    for fb in FORBIDDEN_POSTERS:
        if fb in poster:
            is_forbidden = True
            break
    if is_forbidden:
        continue

    # Filter out tiktokcdn (which expires/403)
    if 'tiktokcdn' in poster or 'tiktokcdn' in str(eps.get('1', '')):
        continue

    # Enforce strict 1-to-1 uniqueness
    poster_clean = poster.split('?')[0]
    if poster_clean in seen_posters:
        continue
    if title.lower() in seen_titles:
        continue

    seen_posters.add(poster_clean)
    seen_titles.add(title.lower())
    cleaned.append(item)

print(f"\nCleaned and fully unique dramas remaining: {len(cleaned)}")

with open(DATA_PATH, 'w', encoding='utf-8') as f:
    json.dump(cleaned, f, ensure_ascii=False, indent=2)

print(f"Saved {len(cleaned)} pristine, 100% unique dramas to {DATA_PATH}!")
