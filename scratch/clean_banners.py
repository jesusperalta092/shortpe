import json

with open('data/dramatube_banners.json', 'r', encoding='utf-8') as f:
    banners = json.load(f)

with open('data/dramatube.json', 'r', encoding='utf-8') as f:
    dramas = json.load(f)

book_id_to_drama = {d.get('bookId'): d for d in dramas if d.get('bookId')}

rep = {
    'Ã¡': 'á', 'Ã©': 'é', 'Ã\xad': 'í', 'Ã­': 'í', 'Ã³': 'ó', 'Ãº': 'ú',
    'Ã‘': 'Ñ', 'Ã±': 'ñ', 'Â¡': '¡', 'Â¿': '¿', 'â€¦': '…', 'Â\xa0': ' '
}

for b in banners:
    t = b['title']
    for k, v in rep.items():
        t = t.replace(k, v)
    b['title'] = t.strip()
    bid = b.get('book_id')
    if bid in book_id_to_drama:
        d = book_id_to_drama[bid]
        b['slug'] = d.get('slug')
        b['total_episodes'] = d.get('total_episodes') or b.get('chapter_count')
    else:
        # Check if drama has bookId in slug
        found = [d for d in dramas if bid in d.get('slug', '')]
        if found:
            b['slug'] = found[0].get('slug')
            b['total_episodes'] = found[0].get('total_episodes') or b.get('chapter_count')

with open('data/dramatube_banners.json', 'w', encoding='utf-8') as f:
    json.dump(banners, f, ensure_ascii=False, indent=2)

print("Banners cleaned:")
for b in banners:
    print(f"  {b['title']} -> slug: {b.get('slug')}, bid: {b.get('book_id')}")
