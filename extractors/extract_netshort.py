# -*- coding: utf-8 -*-
"""
Extractor de NetShort (DramaShorts)
===================================
Uso:  python extractors/extract_netshort.py

Genera: data/netshort.json con la estructura de la seccion DramaShorts.
Prueba inicial: 1 sola serie ("Mi jefa esta obsesionada conmigo").

Para agregar mas series: sumar entradas a SERIES a extraer.
"""
import sys, os, json, time, re

# path al root del proyecto
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from modules import netshort

OUT = os.path.join(ROOT, 'data', 'netshort.json')
POST_DIR = os.path.join(ROOT, 'posters')
os.makedirs(POST_DIR, exist_ok=True)

# ============================================================
# SERIES A EXTRAER
# slug_id: el id final de la URL de NetShort
# ============================================================
SERIES = [
    {
        'slug_id': 'mi-jefa-esta-obsesionada-conmigo-2098613294512787458',
        'slug': 'mi-jefa-esta-obsesionada-conmigo',
        'title': 'Mi Jefa está Obsesionada Conmigo',
        'total_episodes': 40,
        'year': 2026,
        'genres': ['Romance', 'Drama'],
        'description': 'Una intensa historia de amor y obsesión entre una jefa poderosa y su empleado.',
    },
]


def extract_serie(meta):
    slug_id = meta['slug_id']
    total = meta['total_episodes']
    episodes = {}
    print(f'[*] Extrayendo: {meta["title"]} ({total} eps)...', flush=True)
    for n in range(1, total + 1):
        try:
            data = netshort.fetch_episode(slug_id, n)
            if not data or not data.get('video_url'):
                print(f'    ep{n}: sin video', flush=True)
                continue
            episodes[str(n)] = {
                'video': data['video_url'],
                'subtitles': data['subtitles'],
            }
            nsubs = len(data['subtitles'])
            print(f'    ep{n}: OK ({nsubs} subtitulos)', flush=True)
        except Exception as e:
            print(f'    ep{n}: ERROR {str(e)[:50]}', flush=True)
        time.sleep(0.3)

    if not episodes:
        print('[!] No se extrajo ningun episodio', flush=True)
        return None

    return {
        'slug': meta['slug'],
        'slug_id': slug_id,
        'title': meta['title'],
        'description': meta.get('description', ''),
        'genres': meta.get('genres', []),
        'year': meta.get('year', ''),
        'poster': '',
        'poster_local': '',
        'section': 'dramashorts',
        'source': 'netshort',
        'type': 'mp4-vtt',
        'total_episodes': len(episodes),
        'episodes': episodes,
        'subtitle_langs': list(netshort.SUPPORTED_SUBS.keys()),
    }


if __name__ == '__main__':
    print('=' * 50)
    print('Extractor NetShort -> DramaShorts')
    print('=' * 50)
    result = []
    for meta in SERIES:
        s = extract_serie(meta)
        if s:
            result.append(s)
    # guardar
    if os.path.exists(OUT):
        try:
            prev = json.load(open(OUT, encoding='utf-8'))
            # merge sin duplicar por slug
            have = {d['slug'] for d in prev}
            for d in result:
                if d['slug'] not in have:
                    prev.append(d)
            result = prev
        except Exception:
            pass
    json.dump(result, open(OUT, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    print(f'\n[FIN] {len(result)} series guardadas en {OUT}')
