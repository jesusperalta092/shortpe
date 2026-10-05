# -*- coding: utf-8 -*-
"""
Extractor de Narto Drama -> seccion DramaShorts
================================================
Uso:  python extractors/extract_narto.py

Genera: data/narto.json
Prueba inicial: 1 serie ('Owned by My Fiance's Daddy', 60 eps).
Para agregar mas: sumar slugs a SERIES.
"""
import sys, os, json, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from modules import narto

OUT = os.path.join(ROOT, 'data', 'narto.json')
POST_DIR = os.path.join(ROOT, 'posters')
os.makedirs(POST_DIR, exist_ok=True)

# ============================================================
# SERIES A EXTRAER
# ============================================================
SERIES = [
    {
        'slug': 'owned-by-my-fiance-s-daddy',
        'title': 'Owned by My Fiancé’s Daddy',
        'genres': ['Romance', 'Drama'],
        'year': 2026,
    },
]


def extract(meta):
    print(f'[*] Extrayendo: {meta["title"]}...', flush=True)
    data = narto.fetch_serie(meta['slug'])
    if not data or not data.get('episodes'):
        print('    [!] sin datos', flush=True)
        return None
    # descargar poster
    plocal = ''
    if data.get('poster'):
        try:
            fn = f'narto_{meta["slug"][:50]}.jpg'
            path = os.path.join(POST_DIR, fn)
            if not os.path.exists(path):
                import requests
                r = requests.get(data['poster'], headers=narto.HEADERS, timeout=20)
                open(path, 'wb').write(r.content)
            plocal = 'posters/' + fn
        except Exception as e:
            print('    poster fail:', str(e)[:40], flush=True)
    return {
        'slug': meta['slug'],
        'title': meta['title'],
        'description': data.get('description', ''),
        'genres': meta.get('genres', []),
        'year': meta.get('year', ''),
        'poster': data.get('poster', ''),
        'poster_local': plocal,
        'section': 'dramashorts',
        'source': 'narto',
        'type': 'hls',
        'total_episodes': data['total_episodes'],
        'episodes': {k: v['m3u8'] for k, v in data['episodes'].items()},
    }


if __name__ == '__main__':
    print('=' * 50)
    print('Extractor Narto -> DramaShorts')
    print('=' * 50)
    result = []
    for meta in SERIES:
        s = extract(meta)
        if s:
            result.append(s)
            print(f'    OK: {s["total_episodes"]} episodios', flush=True)
    if os.path.exists(OUT):
        try:
            prev = json.load(open(OUT, encoding='utf-8'))
            have = {d['slug'] for d in prev}
            for d in result:
                if d['slug'] not in have:
                    prev.append(d)
            result = prev
        except Exception:
            pass
    json.dump(result, open(OUT, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    print(f'\n[FIN] {len(result)} series en {OUT}')
