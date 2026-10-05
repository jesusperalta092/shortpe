import json
import requests
import re
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

KEY = base64.b64decode('QC6Ir2trghxRAyyyWZEOEFR4GgLhnfQ4A19I3QBlQkc=')
aesgcm = AESGCM(KEY)

def decrypt(enc_str):
    if not enc_str:
        return ''
    try:
        raw = base64.b64decode(enc_str)
        return aesgcm.decrypt(raw[:12], raw[12:], None).decode('utf-8')
    except Exception:
        return ''

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

with open('data/dramatube.json', 'r', encoding='utf-8') as f:
    dramas = json.load(f)

without_subs = [d for d in dramas if not d.get('subtitles')]
print(f"Total dramas without subs in JSON: {len(without_subs)}")

found_count = 0
for i, d in enumerate(without_subs[:15]):
    slug = d.get('original_slug') or d.get('slug').replace('dt-', '')
    book_id = d.get('bookId')
    title = d.get('title')
    page_url = f'https://dramaexpress.net/series/{slug}/episode-1'
    try:
        r = requests.get(page_url, headers=HEADERS, timeout=6)
        if r.status_code == 200:
            # check if bookId exists in text
            m = re.search(r'bookId["\']?\s*:\s*["\']([^"\']+)["\']', r.text)
            actual_book_id = m.group(1) if m else book_id
            
            # Probe episode 1 source
            api_url = f'https://dramaexpress.net/api/episode-source/{actual_book_id}/1'
            api_res = requests.get(api_url, headers={'User-Agent': HEADERS['User-Agent'], 'Referer': page_url}, timeout=6)
            if api_res.status_code == 200:
                desc = (api_res.json() or {}).get('descriptor') or {}
                sub_meta = desc.get('subtitle') or {}
                sub_enc = sub_meta.get('enc')
                sub_url = decrypt(sub_enc) if sub_enc else ''
                print(f"[{i+1}] {title} ({slug}): PAGE OK | bookId={actual_book_id} | Subtitle={'FOUND ('+sub_url[:30]+'...)' if sub_url else 'NONE'}")
                if sub_url:
                    found_count += 1
            else:
                print(f"[{i+1}] {title} ({slug}): PAGE OK but API status {api_res.status_code}")
        else:
            print(f"[{i+1}] {title} ({slug}): Page status {r.status_code}")
    except Exception as e:
        print(f"[{i+1}] {title} ({slug}): Error {e}")

print(f"\nProbing sample finished. Found {found_count} subtitles.")
