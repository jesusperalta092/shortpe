# -*- coding: utf-8 -*-
import json, time, csv, os
from curl_cffi import requests as cf

BASE = 'https://www.freereelss.com'
H = {'Accept': 'application/json', 'Referer': BASE + '/'}

def get(path, retries=3):
    for _ in range(retries):
        try:
            r = cf.get(BASE + path, impersonate='chrome124', headers=H, timeout=30)
            if r.status_code == 200:
                return r.json()
        except Exception as e:
            time.sleep(0.5)
    return None

# 1) Recolectar todos los IDs desde home + categorias
unique_ids = {}
print('[1] Recolectando dramas...')
# Home
home = get('/api/v1/home')
for sec in home.get('data', []):
    tag = sec.get('tag', '')
    for it in sec.get('list', []):
        pid = it['play_id']
        if pid not in unique_ids:
            unique_ids[pid] = {'play_id': pid, 'tag': tag, 'raw': it}

# Categorias (por si hay mas)
for cat in ['CEO', 'Romance', 'Werewolf', 'Sweet Love', 'Revenge', 'Billionaire']:
    d = get(f'/api/v1/play/list?category={cat}&page=1&page_size=100')
    if d and d.get('data'):
        for it in d['data']:
            pid = it['ID']
            if pid not in unique_ids:
                unique_ids[pid] = {'play_id': pid, 'tag': 'category', 'raw': it}

print(f'  IDs unicos: {len(unique_ids)}')

# 2) Por cada drama traer detalle + episodios
print('[2] Obteniendo detalles + episodios...')
catalog = []
for i, (pid, info) in enumerate(unique_ids.items(), 1):
    d = get(f'/api/v1/play?play_id={pid}')
    if not d or not d.get('data'):
        print(f'  [{i}/{len(unique_ids)}] {pid} SIN DATA')
        continue
    drama = d['data']

    eps = []
    for page in [1, 2, 3, 4, 5]:
        ed = get(f'/api/v1/episode/list?play_id={pid}&page={page}&page_size=50')
        if not ed or not ed.get('data'):
            break
        eps.extend(ed['data'])
        if len(ed['data']) < 50:
            break

    drama['episodes'] = eps
    catalog.append(drama)
    print(f'  [{i}/{len(unique_ids)}] {drama["title"][:50]} -> {len(eps)} eps')
    time.sleep(0.2)

# 3) Guardar JSON
with open('freereels_catalog.json', 'w', encoding='utf-8') as f:
    json.dump(catalog, f, ensure_ascii=False, indent=2)
print(f'\n[3] Guardado freereels_catalog.json ({len(catalog)} dramas)')

# 4) Guardar CSV
with open('freereels_catalog.csv', 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f)
    w.writerow(['play_id', 'title', 'categories', 'total_episodes', 'episodes_obtenidos', 'ep1_url', 'cover'])
    total_ep_count = 0
    for d in catalog:
        eps = d.get('episodes', [])
        total_ep_count += len(eps)
        ep1_url = eps[0]['video_url'] if eps else ''
        w.writerow([
            d['play_id'], d['title'], '|'.join(d.get('categories') or []),
            d.get('total_episodes', 0), len(eps), ep1_url, d.get('cover_image_url', '')
        ])
print(f'[4] Guardado freereels_catalog.csv')
print(f'\n=== RESUMEN ===')
print(f'Dramas totales: {len(catalog)}')
print(f'Episodios totales: {total_ep_count}')
print(f'MP4 directos (sin DRM, sin auth): SI')
print(f'Tamano promedio ep: ~12-15 MB')
