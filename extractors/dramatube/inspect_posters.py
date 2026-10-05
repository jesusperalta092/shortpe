import requests, re, json, os, sys
from bs4 import BeautifulSoup

if sys.platform == 'win32':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except: pass

test_slugs = [
    '30-day-bride',
    'craving-the-wrong-brother-2',
    'pregnant-by-the-wrong-twin',
    '100-compatibility',
    'adopted-by-wolves',
    '200-pounds-to-boxing-king',
    '10-million-hunt-for-the-panda'
]

for slug in test_slugs:
    url = f'https://dramaexpress.net/series/{slug}/episode-1'
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Look for the exact cover in the series header / hero
        # In modern websites, check <meta property="og:image">
        og = soup.find('meta', property='og:image')
        og_url = og.get('content') if og else ''
        
        # Check all img tags
        img_tags = [img.get('src') for img in soup.find_all('img') if img.get('src')]
        
        # Check specific book data in script tags
        book_id_match = re.search(r'bookId[\\"]*:\s*[\\"]*([a-zA-Z0-9_-]+)[\\"]*', r.text)
        book_id = book_id_match.group(1) if book_id_match else None
        
        # Also let's check what cover regex matches inside the book context
        cover_match = re.search(r'\"cover\"\s*:\s*\"([^\"]+)\"', r.text)
        cover_val = cover_match.group(1).replace(r'\/', '/') if cover_match else ''
        
        print(f"\n==================== {slug} ====================")
        print(f"BookId: {book_id}")
        print(f"og:image: {og_url}")
        print(f"cover in json: {cover_val}")
        print(f"HTML <img> tags count: {len(img_tags)}")
        for it in img_tags[:5]:
            print(f"  img: {it}")
            
    except Exception as e:
        print(f"Error {slug}: {e}")
