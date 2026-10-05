# -*- coding: utf-8 -*-
"""
Extractor Narto por LOTES -> DramaShorts
=========================================
Lee data/narto_slugs.json, extrae series con checkpoint y verifica que reproduzcan.

Uso:  python extractors/extract_narto_batch.py [cantidad]
"""
import sys, os, json, time, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from modules import narto
import requests

OUT = os.path.join(ROOT, 'data', 'narto.json')
CKPT = os.path.join(ROOT, 'data', 'narto_ckpt.json')
SLUGS = os.path.join(ROOT, 'data', 'narto_slugs.json')
POST_DIR = os.path.join(ROOT, 'posters')
os.makedirs(POST_DIR, exist_ok=True)


def _first_segment(manifest_url, text):
    """Dado un m3u8 (master o directo), devuelve la URL del primer segmento real."""
    base = manifest_url.rsplit('/', 1)[0]
    lines = [l.strip() for l in text.splitlines() if l.strip() and not l.startswith('#')]
    if not lines:
        return None
    first = lines[0]
    full = first if first.startswith('http') else base + '/' + first
    # Si es un sub-playlist (.m3u8), bajar un nivel mas
    if full.split('?')[0].lower().endswith('.m3u8'):
        try:
            r2 = requests.get(full, headers=narto.HEADERS, timeout=15)
            return _first_segment(full, r2.text)
        except Exception:
            return None
    return full


def verify_playable(m3u8_url):
    """Verifica que reproduzca: resuelve hasta el primer segmento y lo baja."""
    try:
        r = requests.get(m3u8_url, headers=narto.HEADERS, timeout=15)
        if r.status_code != 200 or '#EXTM3U' not in r.text:
            return False
        seg_url = _first_segment(m3u8_url, r.text)
        if not seg_url:
            return False
        r3 = requests.get(seg_url, headers=narto.HEADERS, timeout=20)
        return r3.status_code == 200 and len(r3.content) > 1000 and not r3.content.startswith(b'TSENCRY')
    except Exception:
        return False



# Dominios cuyo contenido viene en INGLES (sirven directo)
EN_DOMAINS = ['anyreel', 'reelshort', 'netshort', 'dramabite', 'flex', 'mydrama', 'sereal', 'vigloo', 'flickreels', 'goodshort', 'shortmax', 'starshort', 'joyreels']
# Dominios en indonesio/chino sin subs (descartar)
ID_DOMAINS = ['dramabox', 'dramawave', 'dotdrama', 'cubetv']

def es_contenido_util(episodes):
    """True si el contenido esta en ingles o tiene subtitulos."""
    if not episodes:
        return False
    first = list(episodes.values())[0]
    url = first.get('m3u8', '') if isinstance(first, dict) else str(first)
    low = url.lower()
    # 1) dominio en ingles -> sirve
    for d in EN_DOMAINS:
        if d in low:
            return True
    # 2) tiene subtitulos -> sirve
    if isinstance(first, dict):
        if first.get('subtitles') or first.get('subtitle_url'):
            return True
    # 3) si no es de los indonesios conocidos, aceptar
    for d in ID_DOMAINS:
        if d in low:
            return False
    return True

def extract_one(slug):
    data = narto.fetch_serie(slug)
    if not data or not data.get('episodes'):
        return None
    # FILTRO: solo ingles o con subtitulos
    if not es_contenido_util(data['episodes']):
        return {'slug': slug, 'skip': True, 'reason': 'idioma'}
    # verificar que el primer episodio reproduzca
    first = list(data['episodes'].values())[0]
    if not verify_playable(first['m3u8']):
        return {'slug': slug, 'skip': True}
    # poster
    plocal = ''
    if data.get('poster'):
        try:
            fn = f'narto_{slug[:50]}.jpg'
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
        'description': data.get('description', '')[:400],
        'genres': [],
        'year': '',
        'poster': data.get('poster', ''),
        'poster_local': plocal,
        'section': 'dramashorts',
        'source': 'narto',
        'type': 'hls',
        'total_episodes': data['total_episodes'],
        'episodes': {k: v['m3u8'] for k, v in data['episodes'].items()},
    }


if __name__ == '__main__':
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    slugs = json.load(open(SLUGS, encoding='utf-8'))
    # catalogo actual + checkpoint
    cat = json.load(open(OUT, encoding='utf-8')) if os.path.exists(OUT) else []
    done = set(d['slug'] for d in cat)
    if os.path.exists(CKPT):
        done |= set(json.load(open(CKPT, encoding='utf-8')).get('done', []))
    pending = [s for s in slugs if s not in done]
    print(f'[*] Total:{len(slugs)} | Hechos:{len(done)} | Pendientes:{len(pending)} | Lote:{n}', flush=True)

    added = 0
    skipped = 0
    for i, slug in enumerate(pending[:n], 1):
        try:
            res = extract_one(slug)
            if res is None:
                skipped += 1
                print(f'  [{i}] X {slug[:40]} (sin datos)', flush=True)
            elif res.get('skip'):
                skipped += 1
                print(f'  [{i}] ~ {slug[:40]} (no reproduce)', flush=True)
            else:
                cat.append(res); added += 1
                print(f'  [{i}] OK {res["title"][:40]} | {res["total_episodes"]} eps', flush=True)
            done.add(slug)
        except Exception as e:
            print(f'  [{i}] ERR {slug[:30]} {str(e)[:40]}', flush=True)
        # checkpoint cada 5
        if i % 5 == 0:
            json.dump(cat, open(OUT, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
            json.dump({'done': sorted(done)}, open(CKPT, 'w', encoding='utf-8'))
    json.dump(cat, open(OUT, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    json.dump({'done': sorted(done)}, open(CKPT, 'w', encoding='utf-8'))
    print(f'\n[FIN] +{added} agregados | {skipped} omitidos | Total catalogo: {len(cat)}')
