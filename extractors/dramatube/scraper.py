# -*- coding: utf-8 -*-
"""
DramaTube High-Performance Bulk Scraper
========================================
Extrae dramas de DramaExpress de forma concurrente, desencripta streams HLS y subtítulos,
filtra servidores inestables y guarda directamente en data/dramatube.json con checkpoints.
"""
import os
import sys
import json
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from modules.dramatube import fetch_serie, DATA_PATH

ALL_SLUGS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'dramaexpress_all_slugs.json')


def run_bulk_extraction(limit=100, max_workers=6):
    if not os.path.exists(ALL_SLUGS_FILE):
        print(f"Error: {ALL_SLUGS_FILE} no existe.")
        return

    with open(ALL_SLUGS_FILE, 'r', encoding='utf-8') as f:
        all_slugs = json.load(f)

    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    
    existing = []
    if os.path.exists(DATA_PATH):
        try:
            with open(DATA_PATH, 'r', encoding='utf-8') as f:
                existing = json.load(f)
        except Exception:
            existing = []

    # Mapeo de existentes válidos
    existing_map = {}
    for item in existing:
        orig = item.get('original_slug') or item.get('slug', '').replace('dt-', '')
        if item.get('total_episodes', 0) > 0:
            existing_map[orig] = item

    print(f"=== DramaTube Bulk Extractor ===")
    print(f"Catalog actual: {len(existing_map)} dramas cargados.")
    print(f"Objetivo: Extraer hasta {limit} dramas validos...")

    slugs_to_process = [s for s in all_slugs if s not in existing_map]
    print(f"Dramas pendientes por procesar: {len(slugs_to_process)}")

    results = list(existing_map.values())
    processed = 0
    added = 0
    t0 = time.time()

    def process_slug(slug):
        try:
            item = fetch_serie(slug)
            if item and item.get('total_episodes', 0) > 0:
                # Comprobar que no use servidores inestables
                episodes = item.get('episodes', {})
                ep1_str = str(episodes.get('1', ''))
                if 'goodbos' not in ep1_str and 'shortdizilab' not in ep1_str:
                    return item
            return None
        except Exception:
            return None

    # Procesar por lotes concurrentes
    batch_size = max_workers * 2
    for i in range(0, len(slugs_to_process), batch_size):
        if len(results) >= limit:
            print(f"\nAlcanzada la meta de {limit} dramas!")
            break

        batch = slugs_to_process[i:i + batch_size]
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_slug = {executor.submit(process_slug, s): s for s in batch}
            for future in as_completed(future_to_slug):
                s = future_to_slug[future]
                processed += 1
                try:
                    data = future.result()
                    if data:
                        results.append(data)
                        added += 1
                        title = data.get('title', s)
                        num_eps = data.get('total_episodes', 0)
                        has_subs = len(data.get('subtitles', {})) > 0
                        sub_tag = "[Subs: OK]" if has_subs else "[No Subs]"
                        print(f"[{len(results)}/{limit}] + {title} ({num_eps} eps) {sub_tag}")
                        
                        # Guardar checkpoint inmediatamente
                        with open(DATA_PATH, 'w', encoding='utf-8') as f:
                            json.dump(results, f, ensure_ascii=False, indent=2)
                    else:
                        pass
                except Exception as exc:
                    pass

        # Mostrar progreso
        elapsed = time.time() - t0
        print(f"Progreso: {processed}/{len(slugs_to_process)} analizados | {len(results)} en catalogo | Tiempo: {elapsed:.1f}s")

    print("\n==========================================")
    print(f"EXTRACCION COMPLETADA!")
    print(f"Total en DramaTube: {len(results)} dramas")
    print(f"Archivo guardado en: {DATA_PATH}")
    print("==========================================")


if __name__ == '__main__':
    # Extraer de forma continua todos los dramas disponibles con streams permanentes
    run_bulk_extraction(limit=1000, max_workers=6)
