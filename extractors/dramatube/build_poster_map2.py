# -*- coding: utf-8 -*-
"""Amplia el mapa de posters: crawl masivo de listados + busqueda por titulo."""
import requests, re, json, os, sys, time, urllib.parse
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

mapa = {}
if os.path.exists(OUT):
    try: mapa = json.load(open(OUT, encoding='utf-8'))
    except: mapa = {}
log('mapa inicial: %d' % len(mapa))

d = json.load(open(DT, encoding='utf-8'))
faltan = [x['title'] for x in d if x.get('title','').lower().strip() not in {k.lower().strip() for k in mapa}]
log('titulos sin match: %d' % len(faltan))

# 1) Crawl masivo de listados
urls = []
for p in range(1, 80):
    urls.append('https://dramaexpress.net/series?page=%d' % p)
# 2) Crawl de detalle de cada serie
for x in d:
    urls.append('https://dramaexpress.net/series/'+x['original_slug'])
log('URLs: %d' % len(urls))

with ThreadPoolExecutor(max_workers=12) as ex:
    futs = {ex.submit(crawl, u): u for u in urls}
    done=0; total=len(urls)
    for fu in as_completed(futs):
        done+=1
        for alt, src in fu.result():
            if alt not in mapa:
                mapa[alt] = src
        if done % 40 == 0:
            json.dump(mapa, open(OUT,'w',encoding='utf-8'), ensure_ascii=False)
            log('  %d/%d | mapa: %d' % (done, total, len(mapa)))

# 3) Busqueda por titulo para los que faltan (via /search)
def search(title):
    q = urllib.parse.quote(title[:40])
    for u in ['https://dramaexpress.net/search?q='+q, 'https://dramaexpress.net/series?q='+q]:
        res = crawl(u)
        if res: return res
    return []

log('buscando %d titulos faltantes...' % len(faltan))
with ThreadPoolExecutor(max_workers=8) as ex:
    futs = {ex.submit(search, t): t for t in faltan}
    for fu in as_completed(futs):
        for alt, src in fu.result():
            if alt not in mapa:
                mapa[alt] = src

json.dump(mapa, open(OUT,'w',encoding='utf-8'), ensure_ascii=False)
log('LISTO: %d titulos en mapa' % len(mapa))
