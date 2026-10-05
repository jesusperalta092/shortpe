# -*- coding: utf-8 -*-
"""Extractor cukelis.com v2 (series + peliculas con fuentes)"""
import urllib.request, re, json, os, time, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE='https://cukelis.com'
OUT=r'C:\Users\USER\Downloads\Proyecto_Netflix_Dramas'
POST=os.path.join(OUT,'posters')
os.makedirs(POST,exist_ok=True)
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36'
_tl=threading.local()
def sess():
    if not hasattr(_tl,'s'):
        s=requests.Session()
        s.mount('https://',HTTPAdapter(pool_connections=8,pool_maxsize=8,max_retries=Retry(total=1)))
        s.headers.update({'User-Agent':UA,'Referer':BASE+'/'})
        _tl.s=s
    return _tl.s
LOCK=threading.Lock()

def dec(s):
    try: return s.encode('latin1').decode('utf-8')
    except: return s


def clean_title(t):
    """Limpia el titulo de og:title de cukelis"""
    t=re.sub(r'^Ver\s+','',t)
    t=re.sub(r'\s+(?:en español|en latino|online|gratis|HD|Cukelis).*$','',t,flags=re.I)
    t=re.sub(r'\s*-\s*Cukelis.*$','',t,flags=re.I)
    return t.strip()

def extract_sources(html):
    """Extrae [{hash,lang,label}] del HTML crudo"""
    out=[]
    # patron flexible: hash...lang...label
    rx=re.compile(r'hash[^A-Za-z0-9]{1,8}([A-Za-z0-9_\-]{20,30})[^A-Za-z0-9]{1,8}lang[^A-Za-z0-9]{1,8}([^\\\\"]{2,20})[^A-Za-z0-9]{1,8}label[^A-Za-z0-9]{1,8}([^\\\\"]{2,30})')
    for m in rx.finditer(html):
        out.append({'hash':m.group(1),'lang':dec(m.group(2)),'label':dec(m.group(3))})
    if not out:
        # fallback: solo hashes
        for h in re.findall(r'hash[^A-Za-z0-9]{1,8}([A-Za-z0-9_\-]{20,30})', html):
            out.append({'hash':h,'lang':'Latino','label':''})
    return out

def dl_poster(url, slug, ext='jpg'):
    try:
        fn=f'ck_{slug[:55]}.{ext}'
        path=os.path.join(POST,fn)
        if not os.path.exists(path):
            open(path,'wb').write(sess().get(url,timeout=15).content)
        return 'posters/'+fn
    except: return ''

def extract_pelicula(slug):
    try:
        html=sess().get(f'{BASE}/pelicula/{slug}', timeout=25).text
        if 'No hay fuentes' in html and 'hash' not in html: return None
        tm=re.search(r'og:title" content="([^"]+)"', html)
        title=clean_title(dec(tm.group(1))) if tm else slug.replace('-',' ').title()
        pm=re.search(r'og:image" content="([^"]+)"', html)
        poster=pm.group(1) if pm else ''
        dm=re.search(r'og:description" content="([^"]+)"', html)
        desc=dec(dm.group(1))[:400] if dm else ''
        sources=extract_sources(html)
        if not sources: return None
        ym=re.search(r'"datePublished":"(\d{4})', html)
        year=ym.group(1) if ym else ''
        plocal=dl_poster(poster,slug) if poster else ''
        return {'slug':slug,'title':title,'poster':poster,'poster_local':plocal,
                'description':desc,'genres':[],'year':year,'section':'pelicula',
                'type':'hls-cukelis','sources':sources,
                'total_episodes':1,'episodes':{'1':sources[0]['hash']}}
    except: return None

def extract_serie(slug):
    try:
        html=sess().get(f'{BASE}/serie/{slug}', timeout=25).text
        tm=re.search(r'og:title" content="([^"]+)"', html)
        title=clean_title(dec(tm.group(1))) if tm else slug.replace('-',' ').title()
        pm=re.search(r'og:image" content="([^"]+)"', html)
        poster=pm.group(1) if pm else ''
        dm=re.search(r'og:description" content="([^"]+)"', html)
        desc=dec(dm.group(1))[:400] if dm else ''
        ym=re.search(r'"datePublished":"(\d{4})', html)
        year=ym.group(1) if ym else ''
        # temporadas/episodios disponibles
        eps=set(re.findall(r'/serie/'+re.escape(slug)+r'/temporada-(\d+)/episodio-(\d+)', html))
        if not eps: return None
        eps_sorted=sorted(eps, key=lambda x:(int(x[0]),int(x[1])))
        # extraer hash de cada episodio
        episodes={}
        sources_all=[]
        for (temp,ep) in eps_sorted[:40]:
            try:
                ehtml=sess().get(f'{BASE}/serie/{slug}/temporada-{temp}/episodio-{ep}', timeout=20).text
                srcs=extract_sources(ehtml)
                if srcs:
                    episodes[f'{temp}x{ep}']=srcs[0]['hash']
                    if not sources_all: sources_all=srcs
            except: pass
        if not episodes: return None
        plocal=dl_poster(poster,slug) if poster else ''
        return {'slug':slug,'title':title,'poster':poster,'poster_local':plocal,
                'description':desc,'genres':[],'year':year,'section':'serie',
                'type':'hls-cukelis','sources':sources_all,
                'total_episodes':len(eps_sorted),'episodes':episodes}
    except Exception as e:
        return None

if __name__=='__main__':
    sm=sess().get(f'{BASE}/sitemap.xml', timeout=30).text
    locs=re.findall(r'<loc>([^<]+)</loc>', sm)
    series=set(); pelis=set()
    for u in locs:
        m=re.search(r'/serie/([a-z0-9\-]+)$',u)
        if m: series.add(m.group(1)); continue
        m=re.search(r'/pelicula/([a-z0-9\-]+)$',u)
        if m: pelis.add(m.group(1))
    series=list(series); pelis=list(pelis)
    print(f'[*] cukelis: {len(series)} series | {len(pelis)} peliculas',flush=True)

    result=[]
    # PELICULAS
    print(f'\n[*] Peliculas ({len(pelis)})...',flush=True)
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs={ex.submit(extract_pelicula,s):s for s in pelis}
        for i,f in enumerate(as_completed(futs),1):
            r=f.result()
            if r: result.append(r); print(f'  [{i}] OK peli: {r["title"][:40]}',flush=True)
    # SERIES
    print(f'\n[*] Series ({len(series)})...',flush=True)
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs={ex.submit(extract_serie,s):s for s in series}
        for i,f in enumerate(as_completed(futs),1):
            r=f.result()
            if r: result.append(r); print(f'  [{i}] OK serie: {r["title"][:35]} | {len(r["episodes"])} eps',flush=True)
    json.dump(result, open(os.path.join(OUT,'cukelis.json'),'w',encoding='utf-8'), indent=2, ensure_ascii=False)
    print(f'\n[FIN] {len(result)} titulos: {sum(1 for r in result if r["section"]=="serie")} series + {sum(1 for r in result if r["section"]=="pelicula")} peliculas',flush=True)
