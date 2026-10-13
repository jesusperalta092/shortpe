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
    r = requests.get(sitemap_url, headers=HEADERS, timeout=15)
    urls = re.findall(r'<loc>(.*?)</loc>', r.text)
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
    m = re.search(r'/es/drama/([^/]+)', url)
    if not m: return None
    slug = m.group(1)
    
    for attempt in range(3):
        try:
            # First try /1, fallback to drama root
            r = requests.get(f"https://suikora.com/es/drama/{slug}/1", headers=HEADERS, timeout=15)
            if r.status_code != 200:
                r = requests.get(f"https://suikora.com/es/drama/{slug}", headers=HEADERS, timeout=15)
                if r.status_code != 200:
                    return None
            html = r.text
            
            # Title
            title = None
            h1_m = re.search(r'<h1[^>]*>(?:<a[^>]*>)?(.*?)(?:</a>)?</h1>', html, re.DOTALL)
            if h1_m: title = re.sub(r'<[^>]+>', '', h1_m.group(1)).strip()
            if not title:
                og_t = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', html)
                if og_t: title = og_t.group(1).split(' cap ')[0].split(' - ')[0].strip()
            if not title: title = slug.replace('-', ' ').title()

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

            # 1. Check m3u8
            m3u8s = re.findall(r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*', html)
            video_urls = [u.rstrip('\\').rstrip('"').rstrip("'") for u in m3u8s]
            
            # 2. Check NetShort CDN
            if not video_urls:
                ns_urls = re.findall(r'https://[^\'"\s<>]*netshort\.com/[^\'"\s<>]+', html)
                if ns_urls:
                    video_urls = [u.replace(r'\u0026', '&').rstrip('\\').rstrip('"') for u in ns_urls]
            
            # 3. Check TikTok CDN
            if not video_urls:
                tt_urls = re.findall(r'https://[^\'"\s<>]+tiktokcdn[^\'"\s<>]+', html)
                if tt_urls:
                    video_urls = [u.replace(r'\u0026', '&').rstrip('\\').rstrip('"') for u in tt_urls]
            
            # 4. Check other MP4
            if not video_urls:
                mp4_urls = re.findall(r'https?://[^\s"\'<>]+\.mp4[^\s"\'<>]*', html)
                if mp4_urls:
                    video_urls = [u.replace(r'\u0026', '&').rstrip('\\').rstrip('"') for u in mp4_urls]

            if not video_urls:
                # If still 0 on /1, check root drama page
                r_root = requests.get(f"https://suikora.com/es/drama/{slug}", headers=HEADERS, timeout=10)
                if r_root.status_code == 200:
                    html_root = r_root.text
                    ns = re.findall(r'https://[^\'"\s<>]*netshort\.com/[^\'"\s<>]+', html_root)
                    if ns: video_urls = [u.replace(r'\u0026', '&').rstrip('\\').rstrip('"') for u in ns]
                    if not video_urls:
                        tt = re.findall(r'https://[^\'"\s<>]+tiktokcdn[^\'"\s<>]+', html_root)
                        if tt: video_urls = [u.replace(r'\u0026', '&').rstrip('\\').rstrip('"') for u in tt]

            if not video_urls:
                print(f"[{idx}/{total}] SKIP {slug}: no streams")
                return None
            
            # Remove exact duplicate consecutive URLs
            dedup_urls = []
            for vu in video_urls:
                if not dedup_urls or dedup_urls[-1] != vu:
                    dedup_urls.append(vu)

            episodes = {str(i): u for i, u in enumerate(dedup_urls, 1)}
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
    
    existing = {}
    if os.path.exists(DATA_PATH):
        try:
            for d in json.load(open(DATA_PATH, encoding='utf-8')):
                if d.get('slug') and d.get('episodes'):
                    existing[d['slug']] = d
        except: pass
    print(f"Currently in dramashorts.json: {len(existing)} dramas")

    slugs_to_fetch = []
    for i, u in enumerate(urls, 1):
        m = re.search(r'/es/drama/([^/]+)', u)
        if m and m.group(1) not in existing:
            slugs_to_fetch.append((u, i))

    print(f"Dramas to extract: {len(slugs_to_fetch)} of {total}")
    results = list(existing.values())
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(extract_one, u, idx, total): u for u, idx in slugs_to_fetch}
        for future in as_completed(futures):
            res = future.result()
            if res:
                results.append(res)
                if len(results) % 5 == 0:
                    with open(DATA_PATH, 'w', encoding='utf-8') as f:
                        json.dump(results, f, ensure_ascii=False, indent=2)

    results.sort(key=lambda x: x.get('title', ''))
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\nFINISH! Total now in dramashorts: {len(results)} of {total}")

if __name__ == '__main__':
    main()
