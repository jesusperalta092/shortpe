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

# Parse banners array
m = re.search(r'banners:\s*(\[\{.*?\}\])\s*,\s*tabs:', line87)
if not m:
    # Try finding banners
    m = re.search(r'banners:\s*(\[\{.*?\}\])', line87)

if m:
    banners_str = m.group(1)
    # Convert JS object keys to json keys
    fixed = re.sub(r'([a-zA-Z0-9_]+):', r'"\1":', banners_str)
    try:
        banners = json.loads(fixed)
        print(f"Extracted {len(banners)} banners successfully:")
        for b in banners:
            print(f"  - {b.get('book_title')} (ID: {b.get('book_id')}, eps: {b.get('chapter_count')})")
            print(f"    Pic: {b.get('pic')}")
            print(f"    Book Pic: {b.get('book_pic')}")
    except Exception as e:
        print("Json load error:", e)
        # Regex extract each banner
        for bm in re.finditer(r'\{id:(\d+),title:"(.*?)",pic:"(.*?)",book_id:"(.*?)",book_title:"(.*?)",book_pic:"(.*?)",chapter_count:(\d+),chapter_id:"(.*?)"\}', banners_str):
            print("Regex banner:", bm.group(5), bm.group(4), bm.group(7))
