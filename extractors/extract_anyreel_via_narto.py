# -*- coding: utf-8 -*-
"""
AnyReel via Narto -> DramaShorts (contenido en INGLES)
=======================================================
Las series de AnyReel estan indexadas en Narto (sin el -NNNN final).
Este extractor las baja por la via abierta de Narto.

Uso:  python extractors/extract_anyreel_via_narto.py [cantidad]
"""
import sys, os, json, time, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from modules import narto
import requests

OUT = os.path.join(ROOT, 'data', 'narto.json')
CKPT = os.path.join(ROOT, 'data', 'anyreel_ckpt.json')
SLUGS = os.path.join(ROOT, 'data', 'anyreel_slugs.json')
POST_DIR = os.path.join(ROOT, 'posters')
os.makedirs(POST_DIR, exist_ok=True)


def clean_slug(s):
    """Quita el -NNNN final (6186) -> 'screwing-my-bestie-s-hot-dad'"""
    return re.sub(r'-\d+$', '', s)


def _first_segment(manifest_url, text):
    base = manifest_url.rsplit('/', 1)[0]
    lines = [l.strip() for l in text.splitlines() if l.strip() and not l.startswith('#')]
    if not lines:
        return None
    first = lines[0]
    full = first if first.startswith('http') else base + '/' + first
    if full.split('?')[0].lower().endswith('.m3u8'):
        try:
            r2 = requests.get(full, headers=narto.HEADERS, timeout=15)
            return _first_segment(full, r2.text)
        except Exception:
            return None
    return full


def verify_playable(m3u8_url):
    try:
        r = requests.get(m3u8_url, headers=narto.HEADERS, timeout=15)
        if r.status_code != 200 or '#EXTM3U' not in r.text:
            return False
        seg = _first_segment(m3u8_url, r.text)
        if not seg:
            return False
        r3 = requests.get(seg, headers=narto.HEADERS, timeout=20)
        return r3.status_code == 200 and len(r3.content) > 1000 and not r3.content.startswith(b'TSENCRY')
    except Exception:
        return False


def fetch_via_narto(slug):
    """Baja la serie de Narto (usa el slug sin -NNNN)."""
    url = f'https://narto-drama.com/detail/watch/{slug}/1?lang=es-ES'
    r = requests.get(url, headers=narto.HEADERS, timeout=25)
    if r.status_code != 200:
        return None
    h = r.text.replace('\\/', '/')
    # titulo
    tm = re.search(r'<title>([^<]+?)(?:\s*(?:Episodio|Episode))', h)
    title = tm.group(1).strip() if tm else slug.replace('-', ' ').title()
    # poster
    pm = re.search(r'og:image" content="([^"]+)"', h)
    poster = pm.group(1) if pm else ''
    # descripcion
    dm = re.search(r'og:description" content="[^"]*?—\s*([^"]+)"', h)
    desc = dm.group(1)[:400] if dm else ''
    # episodios (pares numero -> m3u8)
    pairs = re.findall(r'"route_episode_number":(\d+),"number":(\d+),"title":"[^"]*","play_url":"(https://[^"]+?\.m3u8)"', h)
    episodes = {n: u for _, n, u in pairs}
    if not episodes:
        return None
    return {'title': title, 'poster': poster, 'description': desc,
            'total_episodes': len(episodes), 'episodes': episodes}


def extract_one(slug_orig):
    slug = clean_slug(slug_orig)
    data = fetch_via_narto(slug)
    if not data or not data.get('episodes'):
        return None
    # verificar reproduccion
    first = list(data['episodes'].values())[0]
    if not verify_playable(first):
        return {'slug': slug, 'skip': True}
    # poster
    plocal = ''
    if data.get('poster'):
        try:
            fn = f'ar_{slug[:50]}.jpg'
            p = os.path.join(POST_DIR, fn)
            if not os.path.exists(p):
                rr = requests.get(data['poster'], headers=narto.HEADERS, timeout=20)
                open(p, 'wb').write(rr.content)
            plocal = 'posters/' + fn
        except Exception:
            pass
    return {
        'slug': slug,
        'title': data['title'],
        'description': data.get('description', ''),
        'genres': [],
        'year': '',
        'poster': data.get('poster', ''),
        'poster_local': plocal,
        'section': 'dramashorts',
        'source': 'narto',
        'lang': 'en',
        'type': 'hls',
        'total_episodes': data['total_episodes'],
        'episodes': data['episodes'],
    }


if __name__ == '__main__':
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    slugs = json.load(open(SLUGS, encoding='utf-8'))
    cat = json.load(open(OUT, encoding='utf-8')) if os.path.exists(OUT) else []
    done = set(d['slug'] for d in cat)
    if os.path.exists(CKPT):
        done |= set(json.load(open(CKPT, encoding='utf-8')).get('done', []))
    pending = [s for s in slugs if clean_slug(s) not in done]
    print(f'[*] AnyReel: {len(slugs)} total | hechos: {len(done)} | pendientes: {len(pending)} | lote: {n}', flush=True)

    added = 0
    for i, slug in enumerate(pending[:n], 1):
        try:
            res = extract_one(slug)
            if res is None:
                print(f'  [{i}] X {slug[:40]} (sin datos)', flush=True)
            elif res.get('skip'):
                print(f'  [{i}] ~ {slug[:40]} (no reproduce)', flush=True)
            else:
                cat.append(res); added += 1
                print(f'  [{i}] OK {res["title"][:42]} | {res["total_episodes"]} eps', flush=True)
            done.add(clean_slug(slug))
        except Exception as e:
            print(f'  [{i}] ERR {slug[:30]} {str(e)[:40]}', flush=True)
        if i % 5 == 0:
            json.dump(cat, open(OUT, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
            json.dump({'done': sorted(done)}, open(CKPT, 'w', encoding='utf-8'))
    json.dump(cat, open(OUT, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    json.dump({'done': sorted(done)}, open(CKPT, 'w', encoding='utf-8'))
    print(f'\n[FIN] +{added} agregados | Total: {len(cat)}')
