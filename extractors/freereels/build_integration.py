# -*- coding: utf-8 -*-
"""
Integra el catalogo de freereels al proyecto Netflix_Dramas.
- Descarga posters a posters/freereels/
- Genera catalog_freereels.json con formato compatible con server.py
- Copia el catalog.json de la extraccion
"""
import json, os, sys
from curl_cffi import requests as cf

BASE_DIR = r'C:\Users\USER\Downloads\Proyecto_Netflix_Dramas'
POSTERS_DIR = os.path.join(BASE_DIR, 'posters', 'freereels')
EXTRACT_DIR = os.path.join(BASE_DIR, 'extractors', 'freereels')
CATALOG_IN = os.path.join(EXTRACT_DIR, 'catalog.json')
CATALOG_OUT = os.path.join(BASE_DIR, 'catalog_freereels.json')

os.makedirs(POSTERS_DIR, exist_ok=True)

# 1) Cargar catalogo extraido
print('[1] Cargando catalogo...')
catalog = json.load(open(CATALOG_IN, encoding='utf-8'))
print(f'  {len(catalog)} dramas')

H = {'Referer': 'https://www.freereelss.com/'}

# 2) Descargar posters y construir catalogo compatible
print('[2] Descargando posters y generando catalogo...')
out = []
total_ep = 0
for i, d in enumerate(catalog):
    pid = d['play_id']
    title = d['title']
    slug = title.lower()
    # slug ASCII
    import unicodedata
    slug = unicodedata.normalize('NFKD', slug).encode('ascii', 'ignore').decode('ascii')
    slug = ''.join(c if c.isalnum() or c in '- ' else '' for c in slug)
    slug = slug.strip().replace(' ', '-')[:80]
    slug = f'fr-{slug}'

    # Poster
    poster_local = ''
    cover = d.get('cover_image_url', '')
    if cover:
        try:
            r = cf.get(cover, impersonate='chrome124', headers=H, timeout=30)
            if r.status_code == 200:
                ext = 'jpg' if '.jpg' in cover.lower() or 'jpeg' in cover.lower() else 'jpg'
                fname = f'{slug}.{ext}'
                fpath = os.path.join(POSTERS_DIR, fname)
                with open(fpath, 'wb') as f:
                    f.write(r.content)
                poster_local = f'posters/freereels/{fname}'
                print(f'  [{i+1}/{len(catalog)}] poster OK {fname} ({len(r.content)//1024}KB)')
        except Exception as e:
            print(f'  [{i+1}/{len(catalog)}] poster ERR: {e}')

    # Episodios
    eps = d.get('episodes', [])
    episodes = []
    for ep in eps:
        episodes.append({
            'number': ep['episode_number'],
            'title': ep.get('title', ''),
            'video_url': ep['video_url'],
            'episode_id': ep.get('episode_id', ''),
        })
    total_ep += len(episodes)

    out.append({
        'slug': slug,
        'title': title,
        'description': d.get('description', ''),
        'categories': d.get('categories', []),
        'total_episodes': d.get('total_episodes', 0),
        'episodes_count': len(episodes),
        'poster_local': poster_local,
        'poster_remote': cover,
        'source': 'freereels',
        'section': 'DramaShorts',
        'player_type': 'mp4',
        'episodes': episodes,
    })

# 3) Guardar
with open(CATALOG_OUT, 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print(f'\n[3] Guardado {CATALOG_OUT}')
print(f'  Dramas: {len(out)}')
print(f'  Episodios: {total_ep}')
print(f'  Posters: {sum(1 for x in out if x["poster_local"])}')
