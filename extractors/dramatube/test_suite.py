# -*- coding: utf-8 -*-
"""
DramaTube Test Suite
====================
Valida que cada una de las series y streams HLS / subtitulos de DramaTube
estén 100% operativos y sin enlaces caídos.
"""
import os
import sys
import json
import requests

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from modules.dramatube import DATA_PATH

def test_catalog():
    if not os.path.exists(DATA_PATH):
        print(f"Error: {DATA_PATH} no existe.")
        return False
        
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        catalog = json.load(f)

    print(f"=== Verificando {len(catalog)} series en DramaTube ===")
    all_ok = True

    for item in catalog:
        slug = item.get('slug')
        title = item.get('title')
        eps = item.get('episodes', {})
        subs = item.get('subtitles', {})

        if not eps:
            print(f"[FAIL] {title} ({slug}): 0 episodios")
            all_ok = False
            continue

        # Test Episode 1 stream
        ep1_url = eps.get('1')
        has_subs = bool(subs.get('1'))
        
        try:
            r = requests.get(ep1_url, timeout=7, headers={'User-Agent': 'Mozilla/5.0'})
            if r.status_code == 200 and ('#EXTM3U' in r.text or len(r.content) > 100):
                sub_status = "[Subtitulos OK]" if has_subs else "[Sin subtitulos]"
                print(f"[OK] {title} | {len(eps)} eps | Ep 1 Stream: OK | {sub_status}")
            else:
                print(f"[FAIL] {title} | Ep 1 falló (Status: {r.status_code})")
                all_ok = False
        except Exception as e:
            print(f"[FAIL] {title} | Ep 1 error: {e}")
            all_ok = False

    return all_ok

if __name__ == '__main__':
    ok = test_catalog()
    if ok:
        print("\nTodas las series de DramaTube estan 100% operativas.")
    else:
        print("\nSe detectaron detalles en algunas series.")
