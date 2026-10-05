import requests, re, base64, json
from bs4 import BeautifulSoup
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

KEY = base64.b64decode('QC6Ir2trghxRAyyyWZEOEFR4GgLhnfQ4A19I3QBlQkc=')
aesgcm = AESGCM(KEY)

def decrypt(enc_str):
    if not enc_str: return ''
    try:
        raw = base64.b64decode(enc_str)
        return aesgcm.decrypt(raw[:12], raw[12:], None).decode('utf-8')
    except: return ''

r_home = requests.get('https://dramaexpress.net/', headers={'User-Agent': 'Mozilla/5.0'})
slugs = list(set(re.findall(r'/series/([a-zA-Z0-9_-]+)', r_home.text)))

# Also add popular ones
slugs = ['craving-the-wrong-brother-2', 'pregnant-by-the-wrong-twin', 'the-stand-in-bride-refusal', 'my-mafia-husband-doesnt-know-i-speak-italian', 'beg-the-wife-you-threw-away', 'my-stepsons-obsession-after-my-husbands-death', 'bound-to-the-mob-alphas-baby'] + slugs

print(f'Scanning {len(slugs)} dramas on DramaExpress...')
working = []
seen = set()

for slug in slugs:
    if slug in seen: continue
    seen.add(slug)
    page_url = f'https://dramaexpress.net/series/{slug}/episode-1'
    try:
        r = requests.get(page_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=8)
        bm = re.search(r'bookId[\\\"\']*:\s*[\\\"\']*([a-zA-Z0-9_-]+)', r.text)
        if not bm: continue
        bid = bm.group(1)
        
        r_api = requests.get(f'https://dramaexpress.net/api/episode-source/{bid}/1', headers={'User-Agent': 'Mozilla/5.0', 'Referer': page_url}, timeout=8)
        if r_api.status_code != 200: continue
        desc = (r_api.json() or {}).get('descriptor') or {}
        chain = desc.get('chain') or [{}]
        enc = chain[0].get('enc')
        stream_url = decrypt(enc)
        if not stream_url or not stream_url.startswith('http'): continue
        
        # Avoid temporary session signed GCS urls with expiring queries
        if 'goodbos.online' in stream_url or 'shortdizilab.com' in stream_url:
            continue
            
        r_test = requests.get(stream_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=6)
        if r_test.status_code == 200 and len(r_test.text) > 30 and '#EXTM3U' in r_test.text:
            soup = BeautifulSoup(r.text, 'html.parser')
            raw_title = soup.title.string if soup.title else slug
            title = raw_title.split(' Episode 1')[0].split(' - Watch')[0].split(' | DramaExpress')[0].strip()
            working.append((slug, bid, title, stream_url))
            print(f'  [OK 100%] {title} ({slug})')
            if len(working) >= 10:
                break
    except Exception:
        pass

print(f'\nTotal verified 100% working dramas: {len(working)}')
with open('data/verified_working_slugs.json', 'w') as f:
    json.dump(working, f, indent=2)
