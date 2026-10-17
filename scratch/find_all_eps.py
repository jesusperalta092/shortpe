import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('scratch/kurz_ep_raw.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Search for all hrefs
hrefs = set(re.findall(r'href=["\']([^"\']+)["\']', html))
print(f"Total hrefs in episode page: {len(hrefs)}")
ep_hrefs = [h for h in hrefs if '/episodes/' in h]
print(f"Episode hrefs: {len(ep_hrefs)}")
for h in sorted(ep_hrefs)[:10]:
    print("  ", h)

# Search for book_id, drama_id, series_id or similar IDs
ids = re.findall(r'(?:book_id|drama_id|series_id|chapter_id|album_id|bookId|dramaId)["\']?\s*[:=]\s*["\']?([^"\'\s,;]+)', html, re.I)
print("Detected IDs:", set(ids))

# Search for book_cover_batch numbers (which often indicate book/drama id!)
book_nums = set(re.findall(r'book_cover_batch/(\d+)/', html))
print("Book cover batch numbers:", book_nums)

# Search for any API endpoints mentioned in scripts
apis = set(re.findall(r'["\'](/api/[^"\']+)["\']', html))
print("APIs found:", apis)
