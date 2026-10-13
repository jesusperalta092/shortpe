import os
import re
import sys
import json
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_FILE = os.path.join(ROOT, 'data', 'huangguo.json')
POSTERS_DIR = os.path.join(ROOT, 'posters')
NEXT_POSTERS_DIR = os.path.join(ROOT, 'web-next', 'public', 'posters')
os.makedirs(POSTERS_DIR, exist_ok=True)
os.makedirs(NEXT_POSTERS_DIR, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8'
}

def is_spanish_title(title):
    t = title.lower()
    # Reject non-Latin characters (Chinese, Japanese, Korean, Arabic, Cyrillic)
    if re.search(r'[\u4e00-\u9fff\u3040-\u30ff\u0600-\u06ff\u0400-\u04ff]', title):
        return False
    
    es_words = [
        ' de ', ' la ', ' el ', ' en ', ' y ', ' del ', ' las ', ' los ', ' por ', ' un ', ' una ',
        ' con ', ' para ', ' su ', ' al ', ' mi ', ' me ', ' se ', ' te ', ' nos ', ' es ', ' son ',
        'doblado', 'doblada', 'esposa', 'esposo', 'amor', 'reina', 'rey', 'hijo', 'hija', 'padre',
        'madre', 'hermano', 'hermana', 'mafia', 'secreto', 'venganza', 'despierta', 'sueño',
        'matrimonio', 'bebé', 'bebe', 'novia', 'novio', 'vida', 'cielo', 'dios', 'fuego', 'sombra',
        'noche', 'príncipe', 'princesa', 'lobo', 'licántropo', 'dragón', 'dragon', 'contraataque',
        'renacer', 'renacida', 'renacido', 'amo', 'ama', 'casa', 'marido', 'mujer', 'hombre'
    ]
    pad = f" {t} "
    count = sum(1 for w in es_words if w in pad)
    return count >= 1

def download_poster(slug, poster_url):
    if not poster_url: return ""
    local_filename = f"{slug}.jpg"
    local_path = os.path.join(POSTERS_DIR, local_filename)
    next_path = os.path.join(NEXT_POSTERS_DIR, local_filename)
    
    if os.path.exists(local_path) and os.path.getsize(local_path) > 1000:
        if not os.path.exists(next_path):
            try: import shutil; shutil.copy(local_path, next_path)
            except: pass
        return f"/posters/{local_filename}"
        
    try:
        r = requests.get(poster_url, headers=HEADERS, timeout=10)
        if r.status_code == 200 and len(r.content) > 1000:
            with open(local_path, 'wb') as f:
                f.write(r.content)
            try: import shutil; shutil.copy(local_path, next_path)
            except: pass
            return f"/posters/{local_filename}"
    except Exception:
        pass
    return poster_url

def check_one(drama_id):
    url = f"https://huangguodrama.ai/es/video/{drama_id}/"
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        if r.status_code != 200:
            return None
        html = r.text
        
        # 1. Title
        title = None
        h1_m = re.search(r'<h1[^>]*>(.*?)</h1>', html)
        if h1_m:
            title = re.sub(r'<[^>]+>', '', h1_m.group(1)).strip()
            title = re.sub(r'\s*[•·-]\s*Episodio\s*\d+.*$', '', title, flags=re.I).strip()
        if not title:
            t_m = re.search(r'<title>(.*?)</title>', html)
            if t_m:
                title = t_m.group(1).split('•')[0].split('-')[0].split('|')[0].strip()
        if not title or not is_spanish_title(title):
            return None

        # 2. Episodes
        mp4s = re.findall(r'https://(?:huangguo\.chat|media\.huangguodrama\.ai)/motion/drama-episodes/[a-f0-9]+\.mp4', html)
        clean_mp4s = []
        for u in mp4s:
            if not clean_mp4s or clean_mp4s[-1] != u:
                clean_mp4s.append(u)
        
        if len(clean_mp4s) < 2:  # Only count dramas with multiple real episodes
            return None
            
        episodes = {str(i): u for i, u in enumerate(clean_mp4s, 1)}

        # 3. Poster & Description
        poster_m = re.search(r'<meta\s+property="og:image"\s+content="([^"]*)"', html)
        remote_poster = poster_m.group(1).strip() if poster_m else f"https://huangguodrama.ai/covers/d/{drama_id}.jpg"
        
        desc_m = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', html)
        desc = desc_m.group(1).strip() if desc_m else ""

        slug = f"hd-hg-{drama_id}"
        local_poster = download_poster(slug, remote_poster)

        return {
            "slug": slug,
            "title": title,
            "poster": local_poster or remote_poster,
            "description": desc,
            "section": "hotdrama",
            "source": "huangguo",
            "genres": ["HotDrama", "Drama", "Romance"],
            "total_episodes": len(episodes),
            "episodes": episodes
        }
    except Exception as e:
        return None

def main():
    print("Fetching sitemap from huangguodrama.ai...")
    xml = requests.get('https://huangguodrama.ai/sitemap/dramas-es.xml', headers=HEADERS).text
    urls = re.findall(r'<loc>(.*?)</loc>', xml)
    drama_ids = set()
    for u in urls:
        m = re.search(r'/es/(?:detail|video)/(\d+)', u)
        if m: drama_ids.add(m.group(1))

    id_list = sorted(list(drama_ids), key=lambda x: int(x))
    # Make sure target drama 113067 is first!
    if '113067' in id_list:
        id_list.remove('113067')
        id_list.insert(0, '113067')

    print(f"Total unique drama IDs to scan: {len(id_list)}")

    found = []
    start = time.time()
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(check_one, did): did for did in id_list}
        for future in as_completed(futures):
            res = future.result()
            if res:
                found.append(res)
                if len(found) % 10 == 0:
                    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                        json.dump(found, f, ensure_ascii=False, indent=2)
                    print(f"--> Saved {len(found)} dramas to data/huangguo.json")

    # Final save
    found.sort(key=lambda x: x.get('title', ''))
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(found, f, ensure_ascii=False, indent=2)

    total_eps = sum(d['total_episodes'] for d in found)
    print(f"\nScan finished in {time.time()-start:.1f}s!")
    print(f"Total Spanish dramas extracted: {len(found)}")
    print(f"Total playable episodes: {total_eps}")

if __name__ == '__main__':
    main()
