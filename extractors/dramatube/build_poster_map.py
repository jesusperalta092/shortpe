# -*- coding: utf-8 -*-
"""Construye mapa alt(titulo) -> poster correcto, crawleando las cards de dramaexpress."""
import requests, re, json, os, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed

UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36'
H={'User-Agent':UA,'Accept':'text/html,*/*','Referer':'https://dramaexpress.net/'}
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DT = os.path.join(ROOT,'data','dramatube.json')
OUT = os.path.join(ROOT,'data','dt_poster_map.json')

STABLE = ('shorttv','farsun','mydramawave','dramabox','goodshort','crazymaple','netshort','toonshort','rivoshort','stardusttv','aurareeltv','yourwebnovel','cinerrashort','petadrama','vividshort','myluneshort','sixthshort','vyntagetv','allstarcluster','cloudfront','ihappyread','idrama','miraluneshort','dramawave','vigoo','alphashort')

def log(m):
    print(m); sys.stdout.flush()

def crawl(url):
    try:
        r = requests.get(url, headers=H, timeout=15)
        t = r.text.replace('\\/','/').replace('\\','')
        out = []
        for m in re.finditer(r'<img[^>]*alt="([^"]+)"[^>]*src="([^"]+)"', t):
            alt = m.group(1).strip()
            src = m.group(2).replace('&amp;','&')
            if alt and any(c in src for c in STABLE):
                out.append((alt, src))
        return out
    except Exception:
        return []

# cargar mapa existente (reanudable)
mapa = {}
if os.path.exists(OUT):
    try: mapa = json.load(open(OUT, encoding='utf-8'))
    except: mapa = {}

# 1) crawlear series propias (paginas de detalle)
d = json.load(open(DT, encoding='utf-8'))
urls = ['https://dramaexpress.net/series/'+x['original_slug'] for x in d]
# 2) crawlear listados (muchas cards de una)
for p in range(1, 40):
    urls.append('https://dramaexpress.net/series?page=%d' % p)
log('URLs a crawlear: %d' % len(urls))

with ThreadPoolExecutor(max_workers=10) as ex:
    futs = {ex.submit(crawl, u): u for u in urls}
    done=0; total=len(urls)
    for fu in as_completed(futs):
        done+=1
        for alt, src in fu.result():
            if alt not in mapa:
                mapa[alt] = src
        if done % 15 == 0:
            json.dump(mapa, open(OUT,'w',encoding='utf-8'), ensure_ascii=False)
            log('  %d/%d | titulos en mapa: %d' % (done, total, len(mapa)))

json.dump(mapa, open(OUT,'w',encoding='utf-8'), ensure_ascii=False)
log('LISTO: %d titulos en mapa -> %s' % (len(mapa), OUT))
