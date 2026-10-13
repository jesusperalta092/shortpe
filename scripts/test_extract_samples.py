import requests
import re
import json

sample_slugs = [
    "la-madrastra-que-nadie-se-atreve-a-tocar",
    "me-divorcie-y-me-case-con-la-reina-de-la-mafia",
    "doblado-amigas-contra-el-guion"
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8'
}

def extract_drama(slug):
    url = f"https://suikora.com/es/drama/{slug}/1"
    try:
        r = requests.get(url, headers=headers, timeout=12)
        if r.status_code != 200:
            print(f"[{slug}] Status {r.status_code}")
            return None
        html = r.text
        
        # 1. Title
        title = None
        h1_m = re.search(r'<h1[^>]*>(?:<a[^>]*>)?(.*?)(?:</a>)?</h1>', html, re.DOTALL)
        if h1_m:
            title = re.sub(r'<[^>]+>', '', h1_m.group(1)).strip()
        if not title:
            og_t = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', html)
            if og_t:
                title = og_t.group(1).split(' cap ')[0].split(' - ')[0].strip()
        if not title:
            title = slug.replace('-', ' ').capitalize()

        # 2. Description
        desc = ""
        desc_m = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', html)
        if desc_m:
            desc = desc_m.group(1).strip()
            # Clean "Capítulo 1 de X de [Title]. "
            desc = re.sub(r'^Capítulo\s+\d+\s+de\s+\d+\s+de\s+[^.]+\.\s*', '', desc)

        # 3. Poster
        poster = ""
        og_img = re.search(r'<meta\s+property="og:image"\s+content="([^"]*)"', html)
        if og_img:
            poster = og_img.group(1).strip()

        # 4. Episodes (m3u8)
        m3u8_matches = re.findall(r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*', html)
        clean_urls = [u.rstrip('\\').rstrip('"').rstrip("'") for u in m3u8_matches]
        # Deduplicate while preserving order if needed, but in next_f they appear sequentially
        # Let's see if there are duplicates:
        episodes = {str(i): u for i, u in enumerate(clean_urls, 1)}

        return {
            "slug": slug,
            "title": title,
            "description": desc,
            "poster_url": poster,
            "episodes_count": len(episodes),
            "episodes": episodes
        }
    except Exception as e:
        print(f"[{slug}] Error: {e}")
        return None

for s in sample_slugs:
    res = extract_drama(s)
    if res:
        print(f"Drama: {res['title']}")
        print(f"Slug: {res['slug']}")
        print(f"Desc: {res['description'][:80]}...")
        print(f"Poster: {res['poster_url']}")
        print(f"Episodes: {res['episodes_count']}")
        print("-" * 50)
