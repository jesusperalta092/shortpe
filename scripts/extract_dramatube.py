import json
import os
import re
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
HEADERS = {'User-Agent': UA, 'Referer': 'https://www.kurzdrama.com/'}

# Clean shelf display names with emojis from screenshots
SHELF_DISPLAY = {
    'Nuevos Lanzamientos': {'name': 'Nuevos Lanzamientos', 'icon': '✨'},
    'CLASIFICACIÃ“N': {'name': 'CLASIFICACIÓN', 'icon': '🏆'},
    'CLASIFICACIÓN': {'name': 'CLASIFICACIÓN', 'icon': '🏆'},
    'Serie Doblada ðŸŽ™': {'name': 'Serie Doblada 📢', 'icon': '📢'},
    'Serie Doblada 📢': {'name': 'Serie Doblada 📢', 'icon': '📢'},
    'Identidad Oculta ðŸŽ­': {'name': 'Identidad Oculta 🎭', 'icon': '🎭'},
    'Identidad Oculta 🎭': {'name': 'Identidad Oculta 🎭', 'icon': '🎭'},
    'RelaciÃ³n TabÃº': {'name': 'Relación Tabú', 'icon': '💋'},
    'Relación Tabú': {'name': 'Relación Tabú', 'icon': '💋'},
    'BebÃ©s y Embarazos ðŸ ¼': {'name': 'Bebés y Embarazos 🍼', 'icon': '🍼'},
    'Bebés y Embarazos 🍼': {'name': 'Bebés y Embarazos 🍼', 'icon': '🍼'},
    'Amor a Primera Vista ðŸ‘„': {'name': 'Amor a Primera Vista 👄', 'icon': '👄'},
    'Amor a Primera Vista 👄': {'name': 'Amor a Primera Vista 👄', 'icon': '👄'},
    'GÃ©nero Masculino': {'name': 'Género Masculino', 'icon': '⚡'},
    'Género Masculino': {'name': 'Género Masculino', 'icon': '⚡'},
    'Hombre Lobo ðŸ ºy VampiroðŸ§›': {'name': 'Hombre Lobo 🐺 y Vampiro 🧛', 'icon': '🐺'},
    'Hombre Lobo 🐺 y Vampiro 🧛': {'name': 'Hombre Lobo 🐺 y Vampiro 🧛', 'icon': '🐺'},
    'Historias de Asia ðŸŒ ': {'name': 'Historias de Asia 🌏', 'icon': '🌏'},
    'Historias de Asia 🌏': {'name': 'Historias de Asia 🌏', 'icon': '🌏'},
    'MÃ¡s Recomendados': {'name': 'Más Recomendados', 'icon': '🔥'},
    'Más Recomendados': {'name': 'Más Recomendados', 'icon': '🔥'}
}

def clean_shelf_name(sh):
    if sh in SHELF_DISPLAY:
        return SHELF_DISPLAY[sh]['name']
    for k, v in SHELF_DISPLAY.items():
        if k.replace(' ', '').lower() == sh.replace(' ', '').lower():
            return v['name']
    return sh

def clean_text(s):
    if not s: return ''
    # Replace common mojibake
    s = s.replace('Ã¡', 'á').replace('Ã©', 'é').replace('Ã­', 'í').replace('Ã³', 'ó').replace('Ãº', 'ú')
    s = s.replace('Ã±', 'ñ').replace('Ã', 'í').replace('â€¦', '…').replace('Â¡', '¡').replace('Â¿', '¿')
    return s.strip()

def get_book_slug(href):
    t = href.split('/episodes/')[-1].strip('/')
    m = re.search(r'([a-f0-9]{24})', t)
    if not m:
        return None, None
    hex_id = m.group(1)
    prefix = t[:t.index(hex_id)]
    prefix = re.sub(r'^episode-\d+-', '', prefix, flags=re.I).rstrip('-')
    return hex_id, f"{prefix}-{hex_id}"

def main():
    home_path = os.path.join(ROOT, 'scratch', 'kurz_parsed_home.json')
    if not os.path.exists(home_path):
        print("Missing scratch/kurz_parsed_home.json!")
        return

    with open(home_path, 'r', encoding='utf-8') as f:
        home_raw = json.load(f)

    shelves_raw = home_raw['shelves']
    print(f"Loaded {len(shelves_raw)} raw shelves.")

    unique_dramas = {}
    shelf_buckets = {}

    for raw_sh_name, d_list in shelves_raw.items():
        c_sh = clean_shelf_name(raw_sh_name)
        shelf_buckets.setdefault(c_sh, [])

        for d in d_list:
            href = d.get('href', '')
            hex_id, book_slug = get_book_slug(href)
            if not hex_id or not book_slug:
                continue

            slug = f"dt-{book_slug}"
            clean_t = clean_text(d.get('title', ''))

            if slug not in unique_dramas:
                item = {
                    'slug': slug,
                    'title': clean_t,
                    'original_title': clean_t,
                    'bookId': hex_id,
                    'book_slug': book_slug,
                    'first_slug': href.split('/episodes/')[-1].strip('/'),
                    'poster': d.get('image', ''),
                    'shelf': c_sh,
                    'shelves': [c_sh],
                    'source': 'kurzdrama',
                    'section': 'dramatube',
                    'total_episodes': int(d.get('chapter_count', 0)) or 1,
                    'collect_count': int(d.get('collect_count', 0)),
                    'episodes': {}
                }
                unique_dramas[slug] = item
            else:
                if c_sh not in unique_dramas[slug]['shelves']:
                    unique_dramas[slug]['shelves'].append(c_sh)

            if slug not in [x['slug'] for x in shelf_buckets[c_sh]]:
                shelf_buckets[c_sh].append(unique_dramas[slug])

    print(f"Total unique dramas: {len(unique_dramas)}")
    print(f"Total shelves cleaned: {len(shelf_buckets)}")
    for sh, items in shelf_buckets.items():
        print(f"  - [{sh}]: {len(items)} dramas")

    # Scrape all episode slugs concurrently
    print("\nScraping all episode slugs from ReelShort / Kurzdrama...")
    t0 = time.time()

    def scrape_one(item):
        book_slug = item['book_slug']
        url = f"https://www.reelshort.com/es/full-episodes/{book_slug}"
        eps = {}
        try:
            r = requests.get(url, headers={'User-Agent': UA}, timeout=12)
            if r.status_code == 200:
                pages = [1]
                for p in re.findall(r'/full-episodes/[^"\'\s>]+/(\d+)', r.text):
                    pages.append(int(p))
                max_p = max(pages) if pages else 1

                def parse_html(html):
                    soup = BeautifulSoup(html, 'html.parser')
                    for a in soup.find_all('a', href=True):
                        h = a['href']
                        if '/episodes/' in h:
                            ep_slug = h.split('/episodes/')[-1].strip('/')
                            num_m = re.search(r'episode-(\d+)', ep_slug, re.IGNORECASE)
                            num = int(num_m.group(1)) if num_m else 0
                            if num > 0:
                                ep_t = a.get_text(strip=True) or f"Episodio {num}"
                                if str(num) not in eps:
                                    eps[str(num)] = {
                                        'number': num,
                                        'slug': ep_slug,
                                        'title': ep_t,
                                        'm3u8': ''
                                    }

                parse_html(r.text)

                for p in range(2, max_p + 1):
                    rp = requests.get(f"{url}/{p}", headers={'User-Agent': UA}, timeout=12)
                    if rp.status_code == 200:
                        parse_html(rp.text)

        except Exception as e:
            pass

        return item['slug'], eps

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(scrape_one, it): it for it in unique_dramas.values()}
        done_count = 0
        for f in as_completed(futures):
            slug, eps = f.result()
            if eps:
                unique_dramas[slug]['episodes'] = eps
                unique_dramas[slug]['total_episodes'] = max(len(eps), unique_dramas[slug]['total_episodes'])
            done_count += 1
            if done_count % 25 == 0 or done_count == len(unique_dramas):
                print(f"Progress: {done_count}/{len(unique_dramas)} dramas scraped in {time.time()-t0:.1f}s")

    # Fetch m3u8 for target drama "Unida al Alfa y su Beta" Ep 1 to 5
    target_slug = "dt-unida-al-alfa-y-su-beta-6a433648a0263ac457025610"
    if target_slug in unique_dramas:
        t_eps = unique_dramas[target_slug]['episodes']
        for ep_n in ['1', '2', '3', '4', '5']:
            if ep_n in t_eps and t_eps[ep_n].get('slug'):
                try:
                    r_ep = requests.get(f"https://www.kurzdrama.com/es/episodes/{t_eps[ep_n]['slug']}", headers=HEADERS, timeout=8)
                    m = re.search(r'https?://v-mps\.crazymaplestudios\.com/[^\s"\'<>]+\.m3u8', r_ep.text)
                    if m:
                        t_eps[ep_n]['m3u8'] = m.group(0)
                except: pass
        print(f"Pre-cached streams for target drama '{unique_dramas[target_slug]['title']}'")

    # Save to data/dramatube.json
    out_list = list(unique_dramas.values())
    dt_path = os.path.join(DATA_DIR, 'dramatube.json')
    with open(dt_path, 'w', encoding='utf-8') as f:
        json.dump(out_list, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(out_list)} dramas to {dt_path} ({os.path.getsize(dt_path)} bytes)")

    # Save shelf layout metadata
    shelves_data = []
    for sh_name, items in shelf_buckets.items():
        icon = '🎬'
        for k, v in SHELF_DISPLAY.items():
            if v['name'] == sh_name:
                icon = v['icon']
                break
        shelves_data.append({
            'name': sh_name,
            'icon': icon,
            'slug': re.sub(r'[^a-z0-9]+', '-', sh_name.lower()).strip('-'),
            'count': len(items),
            'items': [{
                'slug': x['slug'],
                'title': x['title'],
                'poster': x['poster'],
                'total_episodes': x['total_episodes'],
                'shelf': sh_name
            } for x in items]
        })

    shelves_path = os.path.join(DATA_DIR, 'dramatube_shelves.json')
    with open(shelves_path, 'w', encoding='utf-8') as f:
        json.dump({'shelves': shelves_data, 'total_dramas': len(out_list)}, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(shelves_data)} shelves to {shelves_path}")

if __name__ == '__main__':
    main()
