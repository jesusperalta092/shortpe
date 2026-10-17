import re
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('scratch/kurz_home_raw.html', 'r', encoding='utf-8') as f:
    html = f.read()

line87 = None
for l in html.split('\n'):
    if '__sveltekit_spkrjw.resolve(1' in l:
        line87 = l
        break

# Extract each banner with regex
pattern = r'\{id:(\d+),title:"(.*?)",pic:"(.*?)",book_id:"(.*?)",book_title:"(.*?)",book_pic:"(.*?)",chapter_count:(\d+),chapter_id:"(.*?)"\}'
banners = []
for m in re.finditer(pattern, line87):
    banners.append({
        'id': m.group(1),
        'title': m.group(5),
        'pic': m.group(3),
        'book_id': m.group(4),
        'book_pic': m.group(6),
        'chapter_count': int(m.group(7))
    })

print(f"Extracted {len(banners)} banners:")
for b in banners:
    print(b)

# Save to data/dramatube_banners.json
with open('data/dramatube_banners.json', 'w', encoding='utf-8') as f:
    json.dump(banners, f, ensure_ascii=False, indent=2)
print("Saved to data/dramatube_banners.json")
