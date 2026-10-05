# -*- coding: utf-8 -*-
"""
Extractor Narto FILTRADO -> DramaShorts
========================================
Solo guarda series que:
  1) tengan SUBTITULOS, o
  2) sean de dominio en INGLES (anyreel, r2.cloudflarestorage, stream-e1...)
Y verifica que reproduzcan.

Uso:  python extractors/extract_narto_filtered.py [cantidad]
"""
import sys, os, json, time, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import requests, socket
socket.setdefaulttimeout(15)

OUT = os.path.join(ROOT, 'data', 'narto.json')
CKPT = os.path.join(ROOT, 'data', 'narto_filtered_ckpt.json')
SLUGS = os.path.join(ROOT, 'data', 'narto_slugs.json')
POST_DIR = os.path.join(ROOT, 'posters')
os.makedirs(POST_DIR, exist_ok=True)
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36', 'Referer': 'https://narto-drama.com/'}

# dominios con contenido en INGLES
EN_DOMAINS = ['anyreel', 'r2.cloudflarestorage', 'stream-e1.narto', 'reelshort', 'netshort', 'dramabite', 'flex']


def _first_segment(manifest_url, text):
    base = manifest_url.rsplit('/', 1)[0]
    lines = [l.strip() for l in text.splitlines() if l.strip() and not l.startswith('#')]
    if not lines: return None
    first = lines[0]
    full = first if first.startswith('http') else base + '/' + first
    if full.split('?')[0].lower().endswith('.m3u8'):
        try:
            r2 = requests.get(full, headers=H, timeout=15)
            return _first_segment(full, r2.text)
        except Exception:
            return None
    return full


def verify(m3u8):
    try:
        r = requests.get(m3u8, headers=H, timeout=15)
        if r.status_code != 200 or '#EXTM3U' not in r.text: return False
        seg = _first_segment(m3u8, r.text)
        if not seg: return False
        r3 = requests.get(seg, headers=H, timeout=20)
        return r3.status_code == 200 and len(r3.content) > 1000 and not r3.content.startswith(b'TSENCRY')
    except Exception:
        return False


def process(slug):
    try:
        r = requests.get(f'https://narto-drama.com/detail/watch/{slug}/1?lang=es-ES', headers=H, timeout=25)
        if r.status_code != 200: return ('nodata', None)
        h = r.text.replace('\\/', '/').replace('&amp;', '&')
        # idioma / subtitulos
        has_sub = ('"multi_subtitles":[{' in h) or ('"subtitle_url":"http' in h)
        m = re.search(r'"play_url":"https?://([a-z0-9.\-]+)', h)
        dom = m.group(1) if m else ''
        is_en = any(d in dom for d in EN_DOMAINS)
        if not (has_sub or is_en):
            return ('idioma', None)
        # titulo
        tm = re.search(r'<title>([^<]+?)(?:\s*(?:Episodio|Episode))', h)
        title = tm.group(1).strip() if tm else slug.replace('-', ' ').title()
        pm = re.search(r'og:image" content="([^"]+)"', h)
        poster = pm.group(1) if pm else ''
        dm = re.search(r'og:description" content="[^"]*?—\s*([^"]+)"', h)
        desc = dm.group(1)[:400] if dm else ''
        pairs = re.findall(r'"route_episode_number":(\d+),"number":(\d+),"title":"[^"]*","play_url":"(https://[^"]+?\.m3u8)"', h)
        episodes = {n: u for _, n, u in pairs}
        if not episodes: return ('nodata', None)
        first = list(episodes.values())[0]
        if not verify(first): return ('norepro', None)
        # poster local
        plocal = ''
        if poster:
            try:
                fn = f'nf_{slug[:50]}.jpg'
                p = os.path.join(POST_DIR, fn)
                if not os.path.exists(p):
                    open(p, 'wb').write(requests.get(poster, headers=H, timeout=20).content)
                plocal = 'posters/' + fn
            except Exception: pass
        return ('OK', {
            'slug': slug, 'title': title, 'description': desc, 'genres': [], 'year': '',
            'poster': poster, 'poster_local': plocal, 'section': 'dramashorts', 'source': 'narto',
            'lang': 'en' if is_en else '', 'has_subs': has_sub, 'type': 'hls',
            'total_episodes': len(episodes), 'episodes': episodes,
        })
    except Exception as e:
        return ('err', str(e)[:40])


if __name__ == '__main__':
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    slugs = json.load(open(SLUGS, encoding='utf-8'))
    cat = json.load(open(OUT, encoding='utf-8')) if os.path.exists(OUT) else []
    done = set(d['slug'] for d in cat)
    if os.path.exists(CKPT):
        done |= set(json.load(open(CKPT, encoding='utf-8')).get('done', []))
    pend = [s for s in slugs if s not in done]
    print(f'[*] Total:{len(slugs)} | hechos:{len(done)} | pend:{len(pend)} | lote:{n}', flush=True)
    added = 0; skips = {}
    for i, slug in enumerate(pend[:n], 1):
        st, res = process(slug)
        if st == 'OK':
            cat.append(res); added += 1
            tag = 'EN' if res['lang'] else 'sub'
            print(f'  [{i}] OK({tag}) {res["title"][:40]} | {res["total_episodes"]} eps', flush=True)
        else:
            skips[st] = skips.get(st, 0) + 1
        done.add(slug)
        if i % 5 == 0:
            json.dump(cat, open(OUT, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
            json.dump({'done': sorted(done)}, open(CKPT, 'w', encoding='utf-8'))
    json.dump(cat, open(OUT, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    json.dump({'done': sorted(done)}, open(CKPT, 'w', encoding='utf-8'))
    print(f'\n[FIN] +{added} agregados | omitidos: {skips} | Total: {len(cat)}', flush=True)
