# -*- coding: utf-8 -*-
"""
Scanner de NetShort - verifica que dramas tienen episodios GRATIS y que reproduzcan.
Genera data/netshort_scan.json con el reporte.
"""
import sys, os, json, time, re
import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'data', 'netshort_scan.json')
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
H = {'User-Agent': UA, 'Referer': 'https://netshort.com/'}
BASE = 'https://netshort.com'

def rsc(html):
    c = re.findall(r'self\.__next_f\.push\(\[1,"(.+?)"\]\)', html)
    return ''.join(c).encode().decode('unicode_escape', errors='ignore')

def get_dramas():
    """Lista dramas del home (slug_id + name)."""
    h = requests.get(BASE + '/es', headers=H, timeout=25).text
    r = rsc(h)
    out = []
    for m in re.finditer(r'"shortPlayName":"([^"]+)","shortPlayNameNoHL":"[^"]*","shortPlayNameUrl":"([^"]+)"', r):
        name = m.group(1)
        url = m.group(2)  # /es/episode/slug-ID
        mm = re.search(r'/([a-z0-9\-]+-(\d+))$', url)
        if mm:
            out.append({'name': name, 'slug_id': mm.group(1), 'id': mm.group(2)})
    # dedupe
    seen = set(); uniq = []
    for d in out:
        if d['id'] not in seen:
            seen.add(d['id']); uniq.append(d)
    return uniq

def check_drama(d):
    """Verifica episodios gratis de un drama (hasta 15 para no demorar)."""
    slug_id = d['slug_id']
    total = 0; free = 0; free_nums = []
    # leer la pagina ep1 (trae totalEpisode y lista)
    try:
        r = requests.get(f'{BASE}/es/episode/{slug_id}-ep-1', headers=H, timeout=20)
        rr = rsc(r.text)
    except Exception:
        return None
    m = re.search(r'"totalEpisode":(\d+)', rr)
    total = int(m.group(1)) if m else 0
    # probar primeros 15 episodios
    limit = min(total, 15) if total else 15
    for n in range(1, limit + 1):
        try:
            r = requests.get(f'{BASE}/es/episode/{slug_id}-ep-{n}', headers=H, timeout=15)
            pv = re.search(r'"playVoucher":"([^"]+)"', r.text)
            if pv:
                free += 1; free_nums.append(n)
        except Exception:
            pass
        time.sleep(0.15)
    return {'name': d['name'], 'slug_id': slug_id, 'total': total, 'free_checked': free, 'free_nums': free_nums}

if __name__ == '__main__':
    dramas = get_dramas()
    print(f'[*] {len(dramas)} dramas encontrados. Escaneando primeros 15 de cada uno...', flush=True)
    results = []
    for i, d in enumerate(dramas[:40], 1):
        res = check_drama(d)
        if res:
            results.append(res)
            pct = (res['free_checked'] / min(res['total'] or 15, 15) * 100) if res['total'] else 0
            print(f'  [{i}] {res["name"][:35]:35s} total:{res["total"]:3d} gratis(1-15):{res["free_checked"]:2d} ({pct:.0f}%)', flush=True)
    json.dump(results, open(OUT, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    print(f'\n[FIN] {len(results)} dramas escaneados -> {OUT}')
