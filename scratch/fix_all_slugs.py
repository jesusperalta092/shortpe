import json
import re
import sys
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')

def clean_mojibake(s):
    if not s: return ''
    # Fix double-encoded UTF-8
    try:
        s = s.encode('latin1').decode('utf-8')
    except Exception:
        pass
    rep = {
        'Ã¡': 'á', 'Ã©': 'é', 'Ã­': 'í', 'Ã\xad': 'í', 'Ã³': 'ó', 'Ãº': 'ú',
        'Ã‘': 'Ñ', 'Ã±': 'ñ', 'Â¡': '¡', 'Â¿': '¿', 'â€¦': '…',
        'ðŸŽ™': '📢', 'ðŸŽ­': '🎭', 'ðŸ ¼': '🍼', 'ðŸ‘„': '👄',
        'ðŸ º': '🐺', 'ðŸ§›': '🧛', 'ðŸŒ ': '🌏', 'Â\xa0': ' '
    }
    for k, v in rep.items():
        s = s.replace(k, v)
    return s.strip()

def slugify(text):
    # Normalize unicode to ASCII
    text = clean_mojibake(text)
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text).strip('-')
    return text

with open('data/dramatube.json', 'r', encoding='utf-8') as f:
    dramas = json.load(f)

old_to_new_slugs = {}

for d in dramas:
    d['title'] = clean_mojibake(d.get('title', ''))
    d['original_title'] = d['title']
    
    # Extract hex ID
    bid = d.get('bookId')
    if not bid:
        m = re.search(r'([a-f0-9]{24})', d.get('slug', ''))
        bid = m.group(1) if m else ''
        d['bookId'] = bid
    
    title_slug = slugify(d['title'])
    clean_slug = f"dt-{title_slug}-{bid}" if bid else f"dt-{title_slug}"
    
    old_slug = d['slug']
    old_to_new_slugs[old_slug] = clean_slug
    d['slug'] = clean_slug
    d['book_slug'] = f"{title_slug}-{bid}" if bid else title_slug

print(f"Normalized {len(dramas)} drama slugs.")

# Save data/dramatube.json
with open('data/dramatube.json', 'w', encoding='utf-8') as f:
    json.dump(dramas, f, ensure_ascii=False, indent=2)

# Update data/dramatube_shelves.json
with open('data/dramatube_shelves.json', 'r', encoding='utf-8') as f:
    sh_data = json.load(f)

for sh in sh_data.get('shelves', []):
    for it in sh.get('items', []) + sh.get('all_items', []):
        it['title'] = clean_mojibake(it.get('title', ''))
        old_s = it.get('slug', '')
        if old_s in old_to_new_slugs:
            it['slug'] = old_to_new_slugs[old_s]
        else:
            # find by hex ID
            m = re.search(r'([a-f0-9]{24})', old_s)
            if m:
                hex_id = m.group(1)
                for d in dramas:
                    if d.get('bookId') == hex_id:
                        it['slug'] = d['slug']
                        break

with open('data/dramatube_shelves.json', 'w', encoding='utf-8') as f:
    json.dump(sh_data, f, ensure_ascii=False, indent=2)

# Update data/dramatube_banners.json
with open('data/dramatube_banners.json', 'r', encoding='utf-8') as f:
    banners = json.load(f)

for b in banners:
    b['title'] = clean_mojibake(b.get('title', ''))
    bid = b.get('book_id')
    for d in dramas:
        if d.get('bookId') == bid:
            b['slug'] = d['slug']
            break

with open('data/dramatube_banners.json', 'w', encoding='utf-8') as f:
    json.dump(banners, f, ensure_ascii=False, indent=2)

print("Updated data/dramatube_shelves.json and data/dramatube_banners.json.")

# Sample checks
print("\nSample clean slugs:")
for d in dramas[:8]:
    print(f"  {d['title']} -> {d['slug']}")
