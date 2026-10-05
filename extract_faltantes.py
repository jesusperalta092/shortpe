# -*- coding: utf-8 -*-
"""Extrae solo los dramas faltantes del sitemap de esdramia"""
import urllib.request, re, json, os, time, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE='https://esdramia.com'
OUT=r'C:\Users\USER\Downloads\Proyecto_Netflix_Dramas'
POST=os.path.join(OUT,'posters')
CAT=os.path.join(OUT,'catalog_full.json')
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

def rsc_join(h):
    c=re.findall(r'self\.__next_f\.push\(\[1,"(.+?)"\]\)', h)
    return ''.join(c).encode().decode('unicode_escape', errors='ignore')

def process(slug):
    try:
        detail=sess().get(f'{BASE}/dramas/{slug}', timeout=20).text
        tm=re.search(r'og:title" content="([^"]+)"', detail)
        title=dec(tm.group(1)) if tm else slug.replace('-',' ').title()
        pm=re.search(r'og:image" content="([^"]+)"', detail)
        poster=pm.group(1) if pm else ''
        dm=re.search(r'og:description" content="([^"]+)"', detail)
        desc=dec(dm.group(1))[:400] if dm else ''
        rsc=rsc_join(detail)
        em=re.search(r'"numberOfEpisodes":(\d+)', rsc)
        total=int(em.group(1)) if em else 0
        # hashes
        ep1=sess().get(f'{BASE}/dramas/{slug}/1', timeout=20).text
        hashes=re.findall(r'hash[^0-9a-f]{1,6}([0-9a-f]{32})', ep1)
        # dedupe preservando orden
        seen=set(); uniq=[]
        for h in hashes:
            if h not in seen:
                seen.add(h); uniq.append(h)
        eps={i+1:h for i,h in enumerate(uniq)}
        if not eps: return None
        plocal=''
        if poster:
            try:
                fn=f'p_{slug[:60]}.webp'
                path=os.path.join(POST,fn)
                if not os.path.exists(path):
                    open(path,'wb').write(sess().get(poster,timeout=15).content)
                plocal='posters/'+fn
            except: pass
        return {'slug':slug,'title':title,'poster':poster,'poster_local':plocal,
                'description':desc,'genres':[],'total_episodes':total or len(eps),
                'episode_hashes':{str(k):v for k,v in sorted(eps.items())},'type':'hls','section':'drama'}
    except Exception as e:
        return None

if __name__=='__main__':
    faltan=[s.strip() for s in open(os.path.join(OUT,'faltantes.txt'),encoding='utf-8') if s.strip()]
    print(f'[*] Extrayendo {len(faltan)} faltantes...',flush=True)
    cat=json.load(open(CAT,encoding='utf-8'))
    existing=set(d['slug'] for d in cat)
    nuevos=[]
    with ThreadPoolExecutor(max_workers=6) as ex:
        futs={ex.submit(process,s):s for s in faltan}
        for i,f in enumerate(as_completed(futs),1):
            r=f.result()
            if r and r['slug'] not in existing:
                nuevos.append(r)
                print(f'  [{i}/{len(faltan)}] OK {r["title"][:45]}',flush=True)
            else:
                print(f'  [{i}/{len(faltan)}] X {futs[f]}',flush=True)
    # marcar seccion en todos
    for d in cat:
        if 'section' not in d: d['section']='drama'
    cat.extend(nuevos)
    json.dump(cat, open(CAT,'w',encoding='utf-8'), indent=2, ensure_ascii=False)
    print(f'\n[FIN] Nuevos: {len(nuevos)} | Total: {len(cat)}',flush=True)
