import os, requests, re, json, base64, time
from bs4 import BeautifulSoup
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from concurrent.futures import ThreadPoolExecutor

KEY = base64.b64decode('QC6Ir2trghxRAyyyWZEOEFR4GgLhnfQ4A19I3QBlQkc=')
aesgcm = AESGCM(KEY)

def decrypt(enc_str):
    if not enc_str: return ''
    try:
        raw = base64.b64decode(enc_str)
        return aesgcm.decrypt(raw[:12], raw[12:], None).decode('utf-8')
    except Exception:
        return ''

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8'
}

TARGET_SLUGS = [
    'craving-the-wrong-brother-2',
    'pregnant-by-the-wrong-twin',
    'the-stand-in-bride-refusal',
    'my-mafia-husband-doesnt-know-i-speak-italian',
    'beg-the-wife-you-threw-away',
    'my-stepsons-obsession-after-my-husbands-death',
    'bound-to-the-mob-alphas-baby',
    'ladyaid-from-dumped-pauper-to-tycoon',
    'my-whole-life',
    'shadow-king-and-his-princess'
]

TITLE_MAP = {
    'dt-craving-the-wrong-brother-2': 'Craving the Wrong Brother',
    'dt-pregnant-by-the-wrong-twin': 'Pregnant by the Wrong Twin',
    'dt-the-stand-in-bride-refusal': 'The Stand-In Bride Refusal',
    'dt-my-mafia-husband-doesnt-know-i-speak-italian': "My Mafia Husband Doesn't Know I Speak Italian",
    'dt-beg-the-wife-you-threw-away': 'Beg the Wife You Threw Away',
    'dt-my-stepsons-obsession-after-my-husbands-death': "My Stepson's Obsession After My Husband's Death",
    'dt-bound-to-the-mob-alphas-baby': "Bound to the Mob Alpha's Baby",
    'dt-ladyaid-from-dumped-pauper-to-tycoon': 'LadyAid: From Dumped Pauper to Tycoon',
    'dt-my-whole-life': 'My Whole Life',
    'dt-shadow-king-and-his-princess': 'Shadow King and His Princess'
}

def fetch_single_episode(book_id, ep, referer):
    api_headers = {
        'User-Agent': HEADERS['User-Agent'],
        'Referer': referer,
        'Accept': 'application/json'
    }
    stream_url = None
    subtitles = {}
    
    # 1. Fetch default (English)
    api_url_en = f'https://dramaexpress.net/api/episode-source/{book_id}/{ep}'
    try:
        r = requests.get(api_url_en, headers=api_headers, timeout=10)
        if r.status_code == 200:
            d = (r.json() or {}).get('descriptor') or {}
            enc = (d.get('chain') or [{}])[0].get('enc')
            stream_url = decrypt(enc)
            sub_meta = d.get('subtitle') or {}
            if sub_meta.get('enc'):
                sub_en = decrypt(sub_meta.get('enc'))
                if sub_en:
                    subtitles['en'] = {
                        'url': sub_en,
                        'lang': sub_meta.get('language', 'en-US'),
                        'format': sub_meta.get('format', 'srt'),
                        'label': 'English'
                    }
    except Exception: pass
    
    # 2. If no stream yet, try with lang=es
    if not stream_url:
        api_url_es = f'https://dramaexpress.net/api/episode-source/{book_id}/{ep}?lang=es'
        try:
            r = requests.get(api_url_es, headers=api_headers, timeout=10)
            if r.status_code == 200:
                d = (r.json() or {}).get('descriptor') or {}
                enc = (d.get('chain') or [{}])[0].get('enc')
                stream_url = decrypt(enc)
                sub_meta = d.get('subtitle') or {}
                if sub_meta.get('enc') and 'en' not in subtitles:
                    sub_url = decrypt(sub_meta.get('enc'))
                    if sub_url:
                        subtitles['en'] = {
                            'url': sub_url,
                            'lang': sub_meta.get('language', 'en-US'),
                            'format': sub_meta.get('format', 'srt'),
                            'label': 'English'
                        }
        except Exception: pass
    
    return ep, stream_url, subtitles

os.makedirs('data', exist_ok=True)
output_path = 'data/dramatube.json'
results = []
existing = []
if os.path.exists(output_path):
    try: existing = json.load(open(output_path, encoding='utf-8'))
    except: existing = []

existing_map = {x['original_slug']: x for x in existing if x.get('total_episodes', 0) > 0 and 'goodbos' not in str(x.get('episodes', {})) and 'shortdizilab' not in str(x.get('episodes', {}))}

for idx, slug in enumerate(TARGET_SLUGS, 1):
    custom_slug = f'dt-{slug}'
    if slug in existing_map:
        item = existing_map[slug]
        item['slug'] = custom_slug
        if custom_slug in TITLE_MAP:
            item['title'] = TITLE_MAP[custom_slug]
        results.append(item)
        print(f'[{idx}/{len(TARGET_SLUGS)}] Using valid cached: {item["title"]} ({len(item.get("episodes", {}))} eps)', flush=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        continue

    print(f'[{idx}/{len(TARGET_SLUGS)}] Extracting {slug}...', flush=True)
    page_url = f'https://dramaexpress.net/series/{slug}/episode-1'
    try:
        r = requests.get(page_url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            print(f'  Failed to load {page_url} (status {r.status_code})', flush=True)
            continue
        
        soup = BeautifulSoup(r.text, 'html.parser')
        raw_title = soup.title.string if soup.title else slug
        title = raw_title.split(' Episode 1')[0].split(' - Watch')[0].split(' | DramaExpress')[0].strip()
        if custom_slug in TITLE_MAP:
            title = TITLE_MAP[custom_slug]
        
        desc = ''
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            desc = meta_desc['content']
        
        book_id_match = re.search(r'bookId[\\"]*:\s*[\\"]*([a-zA-Z0-9_-]+)[\\"]*', r.text)
        if not book_id_match:
            print(f'  No bookId found for {slug}', flush=True)
            continue
        book_id = book_id_match.group(1)
        
        poster_match = re.search(r'cover[\\"]*:\s*[\\"]*(https?:[\\/]+[^"\\\s]+)[\\"]*', r.text) or re.search(r'poster[\\"]*:\s*[\\"]*(https?:[\\/]+[^"\\\s]+)[\\"]*', r.text)
        poster = poster_match.group(1).replace(r'\/', '/') if poster_match else ''
        if not poster:
            og_img = soup.find('meta', property='og:image')
            if og_img and og_img.get('content'):
                poster = og_img['content']
        
        ep_numbers = [int(x) for x in re.findall(r'serial_number[\\"]*:\s*(\d+)', r.text)]
        total_episodes = max(ep_numbers) if ep_numbers else 1
        
        print(f'  Title: "{title}" | BookID: {book_id} | Total Eps: {total_episodes}', flush=True)
        
        episodes_dict = {}
        subtitles_dict = {}
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(fetch_single_episode, book_id, ep, page_url) for ep in range(1, total_episodes + 1)]
            for fut in futures:
                ep_num, stream, subs = fut.result()
                if stream and 'goodbos' not in stream and 'shortdizilab' not in stream:
                    episodes_dict[str(ep_num)] = stream
                if subs:
                    subtitles_dict[str(ep_num)] = subs
        
        print(f'  [OK] Extracted {len(episodes_dict)}/{total_episodes} streamable episodes', flush=True)
        
        item = {
            'slug': custom_slug,
            'original_slug': slug,
            'bookId': book_id,
            'title': title,
            'description': desc,
            'poster': poster,
            'poster_local': '',
            'section': 'dramatube',
            'source': 'dramatube',
            'total_episodes': len(episodes_dict),
            'genres': ['Drama', 'Romance', 'DramaTube'],
            'lang': 'en',
            'episodes': episodes_dict,
            'subtitles': subtitles_dict
        }
        
        results.append(item)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        print(f'  Error extracting {slug}: {e}', flush=True)

print(f'\n========================================', flush=True)
print(f'Extracted {len(results)} DramaTube dramas to {output_path}!', flush=True)
print(f'========================================', flush=True)
