import requests
import json
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
r = requests.get('https://www.reelshort.com/es', headers={'User-Agent': UA}, timeout=10)

next_data = re.search(r'<script id="__NEXT_DATA__" type="application/json">([^<]+)</script>', r.text)
d = json.loads(next_data.group(1))
web_info = d['props']['pageProps']['fallback']['/api/ms/hall/webInfo']

shelves = web_info['bookShelfList']
print(f"Total shelves in ReelShort /es: {len(shelves)}")

all_books = {}
for i, sh in enumerate(shelves):
    title = sh.get('title') or sh.get('name') or sh.get('shelf_name')
    books = sh.get('books') or sh.get('book_list') or sh.get('list') or []
    print(f"Shelf {i+1}: '{title}' -> {len(books)} books")
    for b in books:
        bid = b.get('book_id') or b.get('id')
        btitle = b.get('book_title') or b.get('title')
        if bid and bid not in all_books:
            all_books[bid] = b

print(f"\nTotal unique books in ReelShort /es homepage: {len(all_books)}")

# Now check if ReelShort has an API to get more books or categories!
# Let's inspect the API endpoints ReelShort calls
