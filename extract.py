import urllib.request, re, json, os, time

BASE='https://esdramia.com'
OUT=r'C:\Users\USER\Downloads\Proyecto_Netflix_Dramas'
HDRS={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'}
JHDRS=dict(HDRS, Accept='application/json', Referer=BASE+'/')

def get(url, hdrs=HDRS, timeout=40):
    req=urllib.request.Request(url, headers=hdrs)
    return urllib.request.urlopen(req, timeout=timeout).read().decode('utf-8','ignore')

def rsc_join(html):
    chunks=re.findall(r'self\.__next_f\.push\(\[1,"(.+?)"\]\)', html)
    return ''.join(chunks).encode().decode('unicode_escape', errors='ignore')

def decode_esc(s):
    try: return s.encode('latin1').decode('utf-8')
    except: return s

home=get(BASE+'/')
slugs=[]
for m in re.finditer(r'/dramas/([a-z0-9\-]+)["\'?#]', home):
    s=m.group(1)
    if s not in slugs and s!='dramas': slugs.append(s)

result=[]
for slug in slugs:
    if len(result)>=10: break
    try:
        detail=get(f'{BASE}/dramas/{slug}')
        # titulo desde og:title
        tm=re.search(r'og:title" content="([^"]+)"', detail)
        title=decode_esc(tm.group(1)) if tm else slug.replace('-',' ').title()
        # poster desde og:image
        pm=re.search(r'og:image" content="([^"]+)"', detail)
        poster=pm.group(1) if pm else ''
        # descripcion
        dm=re.search(r'og:description" content="([^"]+)"', detail)
        desc=decode_esc(dm.group(1))[:400] if dm else ''
        rsc=rsc_join(detail)
        em=re.search(r'"numberOfEpisodes":(\d+)', rsc)
        total=int(em.group(1)) if em else 0
        # generos del JSON-LD
        genres=[]
        gm=re.search(r'"genre":\s*\[([^\]]+)\]', rsc)
        if gm: genres=[decode_esc(g) for g in re.findall(r'"([^"]+)"', gm.group(1))]
        if not genres:
            gm2=re.search(r'"genre":\s*"([^"]+)"', rsc)
            if gm2: genres=[decode_esc(gm2.group(1))]
        # ep 1 hash
        ep1=get(f'{BASE}/dramas/{slug}/1')
        hm=re.search(r'"hash":"([0-9a-f]{32})"', rsc_join(ep1))
        if not hm:
            print(f'   x {slug}: sin hash'); continue
        ep_hash=hm.group(1)
        data=json.loads(get(f'{BASE}/api/stream/{ep_hash}', JHDRS, 25))
        vpath=data['sources'][0]['url']
        result.append({'slug':slug,'title':title,'poster':poster,'description':desc,'genres':genres,'total_episodes':total,'episode':1,'hash':ep_hash,'stream_path':vpath,'type':data.get('type','file')})
        print(f'   OK {len(result):2d}. {title[:45]:45s} | {total:3d} eps | {vpath[:45]}')
        time.sleep(0.3)
    except Exception as e:
        print(f'   x {slug}: {str(e)[:70]}')

json.dump(result, open(os.path.join(OUT,'catalog.json'),'w',encoding='utf-8'), indent=2, ensure_ascii=False)
print(f'\n[OK] {len(result)} dramas guardados en catalog.json')
