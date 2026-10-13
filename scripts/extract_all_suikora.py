import os
import re
import sys
import json
import time
import shutil
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(ROOT, 'data', 'dramashorts.json')
POSTERS_DIR = os.path.join(ROOT, 'posters')
NEXT_POSTERS_DIR = os.path.join(ROOT, 'web-next', 'public', 'posters')
os.makedirs(POSTERS_DIR, exist_ok=True)
os.makedirs(NEXT_POSTERS_DIR, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8'
}

def get_sitemap_urls():
    sitemap_url = 'https://suikora.com/sitemap/dramas-es-0.xml'
    print(f"Fetching sitemap from {sitemap_url}...")
    r = requests.get(sitemap_url, headers=HEADERS, timeout=15)
    urls = re.findall(r'<loc>(.*?)</loc>', r.text)
    print(f"Total drama URLs in sitemap: {len(urls)}")
    return urls

def infer_genres(title, desc):
    text = (title + " " + desc).lower()
    genres = ['Drama']
    if any(k in text for k in ['amor', 'romance', 'boda', 'casar', 'esposa', 'esposo', 'novia', 'novio', 'beso', 'pareja']):
        genres.append('Romance')
    if any(k in text for k in ['venganza', 'vengar', 'traicion', 'traición', 'renacer', 'renacida', 'renacido']):
        genres.append('Venganza')
    if any(k in text for k in ['ceo', 'magnate', 'multimillonario', 'millonario', 'heredero', 'heredera', 'empresario']):
        genres.append('CEO')
    if any(k in text for k in ['mafia', 'don', 'crimen', 'peligroso', 'capo']):
        genres.append('Mafia')
    if any(k in text for k in ['colegio', 'escuela', 'estudiante', 'profesor', 'universidad']):
        genres.append('Escolar')
    if any(k in text for k in ['dragón', 'dragon', 'dios', 'fénix', 'fenix', 'magia', 'apocalipsis', 'sobrenatural']):
        genres.append('Fantasía')
    genres.append('DramaShorts')
    return list(dict.fromkeys(genres))

def download_poster(slug, poster_url):
    if not poster_url:
        return ""
    local_filename = f"{slug}.webp"
    local_path = os.path.join(POSTERS_DIR, local_filename)
    next_path = os.path.join(NEXT_POSTERS_DIR, local_filename)
    
    if os.path.exists(local_path) and os.path.getsize(local_path) > 1000:
        if not os.path.exists(next_path):
            try: shutil.copy(local_path, next_path)
            except: pass
        return f"/posters/{local_filename}"
        
    try:
        r = requests.get(poster_url, headers=HEADERS, timeout=10)
        if r.status_code == 200 and len(r.content) > 1000:
            with open(local_path, 'wb') as f:
                f.write(r.content)
            try: shutil.copy(local_path, next_path)
            except: pass
            return f"/posters/{local_filename}"
    except Exception as e:
        pass
    return poster_url

def extract_one(url, idx, total):
    # Extract slug
    m = re.search(r'/es/drama/([^/]+)', url)
    if not m:
        return None
    slug = m.group(1)
    page_url = f"https://suikora.com/es/drama/{slug}/1"
    
    for attempt in range(3):
        try:
            r = requests.get(page_url, headers=HEADERS, timeout=15)
            if r.status_code != 200:
                # Try root drama url
                r = requests.get(f"https://suikora.com/es/drama/{slug}", headers=HEADERS, timeout=15)
                if r.status_code != 200:
                    print(f"[{idx}/{total}] ERR {slug}: status {r.status_code}")
                    return None
            html = r.text
            
            # Title
            title = None
            h1_m = re.search(r'<h1[^>]*>(?:<a[^>]*>)?(.*?)(?:</a>)?</h1>', html, re.DOTALL)
            if h1_m:
                title = re.sub(r'<[^>]+>', '', h1_m.group(1)).strip()
            if not title:
                og_t = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', html)
                if og_t:
                    title = og_t.group(1).split(' cap ')[0].split(' - ')[0].strip()
            if not title:
                title = slug.replace('-', ' ').title()

            # Description
            desc = ""
            desc_m = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', html)
            if desc_m:
                desc = desc_m.group(1).strip()
                desc = re.sub(r'^Capítulo\s+\d+\s+de\s+\d+\s+de\s+[^.]+\.\s*', '', desc)

            # Poster
            og_img = re.search(r'<meta\s+property="og:image"\s+content="([^"]*)"', html)
            remote_poster = og_img.group(1).strip() if og_img else ""
            local_poster = download_poster(slug, remote_poster)

            # Episodes
            m3u8_matches = re.findall(r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*', html)
            clean_urls = [u.rstrip('\\').rstrip('"').rstrip("'") for u in m3u8_matches]
            if not clean_urls:
                print(f"[{idx}/{total}] WARN {slug}: 0 episodes found")
                return None
            
            episodes = {str(i): u for i, u in enumerate(clean_urls, 1)}
            genres = infer_genres(title, desc)

            item = {
                "slug": slug,
                "title": title,
                "poster": local_poster or remote_poster,
                "description": desc,
                "section": "dramashorts",
                "source": "suikora",
                "genres": genres,
                "total_episodes": len(episodes),
                "episodes": episodes
            }
            print(f"[{idx}/{total}] OK: {title} ({len(episodes)} eps)")
            return item
        except Exception as e:
            if attempt == 2:
                print(f"[{idx}/{total}] FAIL {slug}: {e}")
                return None
            time.sleep(1)

def main():
    urls = get_sitemap_urls()
    total = len(urls)
    
    # Load existing items to avoid re-extracting if already complete
    existing = {}
    if os.path.exists(DATA_PATH):
        try:
            for d in json.load(open(DATA_PATH, encoding='utf-8')):
                if d.get('slug') and d.get('episodes'):
                    existing[d['slug']] = d
        except: pass
    print(f"Already existing in dramashorts.json: {len(existing)} dramas")

    results = list(existing.values())
    slugs_to_fetch = []
    for i, u in enumerate(urls, 1):
        m = re.search(r'/es/drama/([^/]+)', u)
        if m and m.group(1) not in existing:
            slugs_to_fetch.append((u, i))

    print(f"Remaining dramas to extract: {len(slugs_to_fetch)} of {total}")
    
    start_time = time.time()
    extracted_count = 0

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(extract_one, u, idx, total): u for u, idx in slugs_to_fetch}
        for future in as_completed(futures):
            res = future.result()
            if res:
                results.append(res)
                extracted_count += 1
                # Save progress periodically every 10 items
                if extracted_count % 10 == 0:
                    with open(DATA_PATH, 'w', encoding='utf-8') as f:
                        json.dump(results, f, ensure_ascii=False, indent=2)
                    print(f"--> Saved progress: {len(results)} dramas in data/dramashorts.json")

    # Final save
    # Sort by title
    results.sort(key=lambda x: x.get('title', ''))
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    total_eps = sum(d.get('total_episodes', 0) for d in results)
    elapsed = time.time() - start_time
    print(f"\n==========================================")
    print(f"EXTRACTION COMPLETE!")
    print(f"Total dramas in DramaShorts: {len(results)}")
    print(f"Total episodes: {total_eps}")
    print(f"Elapsed time: {elapsed:.1f} seconds")
    print(f"==========================================")

if __name__ == '__main__':
    main()
