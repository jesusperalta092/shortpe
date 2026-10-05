# -*- coding: utf-8 -*-
"""Extractor masivo esdramia.com - ROBUSTO: guardado incremental, timeout por item"""
import urllib.request, re, json, os, time, sys, threading, signal
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError as FTimeout

BASE='https://esdramia.com'
OUT=r'C:\Users\USER\Downloads\Proyecto_Netflix_Dramas'
POST=os.path.join(OUT,'posters')
os.makedirs(POST,exist_ok=True)
CAT=os.path.join(OUT,'catalog_full.json')
CKPT=os.path.join(OUT,'_checkpoint.json')
H={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'}
JH=dict(H, Accept='application/json', Referer=BASE+'/')
SAVE_LOCK=threading.Lock()

def get(url, hdrs=H, timeout=20):
    return urllib.request.urlopen(urllib.request.Request(url,headers=hdrs),timeout=timeout).read()

def dec(s):
    try: return s.encode('latin1').decode('utf-8')
    except: return s

def rsc_join(html):
    chunks=re.findall(r'self\.__next_f\.push\(\[1,"(.+?)"\]\)', html)
    return ''.join(chunks).encode().decode('unicode_escape', errors='ignore')

def fetch_all_episode_hashes(slug):
    html=get(f'{BASE}/dramas/{slug}/1', timeout=18).decode('utf-8','ignore')
    # captura {id, hash, title, episodeNumber} en cualquier orden
    eps={}
    for m in re.finditer(r'\\"id\\":(\\d+),\\"hash\\":\\"([0-9a-f]{32})\\",\\"title\\":\\"([^\\"]*)\\",\\"episodeNumber\\":(\\d+)', html):
        eps[int(m.group(4))]=m.group(2)
    if not eps:
        # fallback: hash + episodeNumber
        for m in re.finditer(r'\\"hash\\":\\"([0-9a-f]{32})\\",\\"title\\":\\"[^\\"]*\\",\\"episodeNumber\\":(\\d+)', html):
            eps[int(m.group(2))]=m.group(1)
    if not eps:
        # ultimo fallback: solo hashes en orden
        hashes=re.findall(r'\\"hash\\":\\"([0-9a-f]{32})\\"', html)
        for i,h in enumerate(hashes,1): eps[i]=h
    return eps

def process_drama(slug):
    try:
        detail=get(f'{BASE}/dramas/{slug}', timeout=18).decode('utf-8','ignore')
        tm=re.search(r'og:title" content="([^"]+)"', detail)
        title=dec(tm.group(1)) if tm else slug.replace('-',' ').title()
        pm=re.search(r'og:image" content="([^"]+)"', detail)
        poster=pm.group(1) if pm else ''
        dm=re.search(r'og:description" content="([^"]+)"', detail)
        desc=dec(dm.group(1))[:400] if dm else ''
        rsc=rsc_join(detail)
        em=re.search(r'"numberOfEpisodes":(\d+)', rsc)
        total=int(em.group(1)) if em else 0
        genres=[]
        gm=re.search(r'"genre":\s*\[([^\]]+)\]', rsc)
        if gm: genres=[dec(g) for g in re.findall(r'"([^"]+)"', gm.group(1))]
        if not genres:
            gm2=re.search(r'"genre":\s*"([^"]+)"', rsc)
            if gm2: genres=[dec(gm2.group(1))]
        ep_hashes=fetch_all_episode_hashes(slug)
        if not ep_hashes: return None
        plocal=''
        if poster:
            try:
                fn=f'p_{slug[:60]}.webp'
                path=os.path.join(POST,fn)
                if not os.path.exists(path):
                    open(path,'wb').write(get(poster,timeout=15))
                plocal='posters/'+fn
            except: pass
        return {
            'slug':slug,'title':title,'poster':poster,'poster_local':plocal,
            'description':desc,'genres':genres,'total_episodes':total or len(ep_hashes),
            'episode_hashes':{str(k):v for k,v in sorted(ep_hashes.items())},'type':'hls'
        }
    except Exception as e:
        return {'slug':slug,'error':str(e)[:80]}

# ==== ESTADO GLOBAL ====
CATALOG=[]
DONE=set()
CK={'done_slugs':[]}

def load():
    global CATALOG, DONE, CK
    if os.path.exists(CAT):
        try: CATALOG=json.load(open(CAT,encoding='utf-8'))
        except: CATALOG=[]
    if os.path.exists(CKPT):
        try: CK=json.load(open(CKPT,encoding='utf-8'))
        except: CK={'done_slugs':[]}
    DONE=set(d['slug'] for d in CATALOG if 'slug' in d)
    DONE.update(CK.get('done_slugs',[]))

def save_atomic():
    with SAVE_LOCK:
        tmp=CAT+'.tmp'
        json.dump(CATALOG, open(tmp,'w',encoding='utf-8'), indent=2, ensure_ascii=False)
        os.replace(tmp, CAT)
        CK['done_slugs']=list(DONE)
        tmp2=CKPT+'.tmp'
        json.dump(CK, open(tmp2,'w',encoding='utf-8'))
        os.replace(tmp2, CKPT)

if __name__=='__main__':
    load()
    sm=get(f'{BASE}/sitemap.xml',timeout=30).decode('utf-8','ignore')
    urls=[u for u in re.findall(r'<loc>([^<]+)</loc>',sm) if u.startswith(BASE+'/dramas/') and u.count('/')==4]
    slugs=[u.rsplit('/',1)[-1] for u in urls]
    pending=[s for s in slugs if s not in DONE]
    print(f'[*] Total: {len(slugs)} | Ya hechos: {len(DONE)} | Pendientes: {len(pending)}', flush=True)
    if not pending:
        print('[FIN] Nada por hacer'); sys.exit(0)

    BATCH=int(sys.argv[1]) if len(sys.argv)>1 else 40
    batch=pending[:BATCH]
    print(f'[*] Lote: {len(batch)} dramas con 6 hilos, timeout 30s/item', flush=True)

    results=[]
    with ThreadPoolExecutor(max_workers=6) as ex:
        futs={ex.submit(process_drama,s):s for s in batch}
        for i,f in enumerate(as_completed(futs),1):
            slug=futs[f]
            try:
                r=f.result(timeout=30)
            except Exception as e:
                r={'slug':slug,'error':'timeout/err '+str(e)[:50]}
            if r is None:
                DONE.add(slug)
                continue
            if 'error' in r:
                print(f'  [{i}/{len(batch)}] X {slug}: {r["error"]}',flush=True)
                # NO marcamos como hecho; se reintentara
            else:
                CATALOG.append(r); DONE.add(slug)
                print(f'  [{i}/{len(batch)}] OK {r["title"][:45]:45s} | {len(r["episode_hashes"])} eps',flush=True)
            if i%10==0:
                save_atomic()
    save_atomic()
    print(f'\n[FIN] Catalogo: {len(CATALOG)} dramas | {sum(len(d.get("episode_hashes",{})) for d in CATALOG)} eps | Faltan: {len(slugs)-len(DONE)}',flush=True)
