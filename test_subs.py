import json, requests, base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

KEY = base64.b64decode('QC6Ir2trghxRAyyyWZEOEFR4GgLhnfQ4A19I3QBlQkc=')
aesgcm = AESGCM(KEY)

def decrypt(enc_str):
    if not enc_str: return ''
    try:
        raw = base64.b64decode(enc_str)
        return aesgcm.decrypt(raw[:12], raw[12:], None).decode('utf-8')
    except Exception:
        return ''

d = json.load(open('data/dramatube.json', encoding='utf-8'))
for item in d:
    slug = item.get('original_slug') or item.get('slug').replace('dt-', '')
    book_id = item.get('bookId')
    page_url = f'https://dramaexpress.net/series/{slug}/episode-1'
    
    # 1. Test with lang=es
    r_es = requests.get(f'https://dramaexpress.net/api/episode-source/{book_id}/1?lang=es', headers={'User-Agent': 'Mozilla/5.0', 'Referer': page_url})
    sub_es_url = ''
    sub_es_meta = {}
    if r_es.status_code == 200:
        desc = (r_es.json() or {}).get('descriptor') or {}
        sub_es_meta = desc.get('subtitle') or {}
        sub_es_url = decrypt(sub_es_meta.get('enc'))
        
    # 2. Test default (en)
    r_en = requests.get(f'https://dramaexpress.net/api/episode-source/{book_id}/1', headers={'User-Agent': 'Mozilla/5.0', 'Referer': page_url})
    sub_en_url = ''
    sub_en_meta = {}
    if r_en.status_code == 200:
        desc = (r_en.json() or {}).get('descriptor') or {}
        sub_en_meta = desc.get('subtitle') or {}
        sub_en_url = decrypt(sub_en_meta.get('enc'))
        
    print(f"Drama: {item['title']}")
    print(f"  ES Sub: {sub_es_meta.get('language')} | {sub_es_url[:60] if sub_es_url else 'None'}")
    print(f"  EN Sub: {sub_en_meta.get('language')} | {sub_en_url[:60] if sub_en_url else 'None'}")
