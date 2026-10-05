# -*- coding: utf-8 -*-
"""Scan rapido de dramas cifrados (timeout agresivo, threads)"""
import urllib.request, json, os, concurrent.futures, sys

ROOT=r'C:\Users\USER\Downloads\Proyecto_Netflix_Dramas'
CAT=os.path.join(ROOT,'catalog_full.json')
B='http://127.0.0.1:8090'

def check(drama):
    slug=drama['slug']
    try:
        d=json.loads(urllib.request.urlopen(B+f'/proxy/episode?slug={slug}&ep=1',timeout=12).read())
        if d.get('player_type')=='file':
            return (slug,'ok',None)
        # HLS: usar el player_url (manifest ya reescrito)
        man=urllib.request.urlopen(B+d['player_url'],timeout=12).read().decode()
        subs=[l for l in man.splitlines() if l.startswith('/proxy/manifest')]
        if subs:
            sub=urllib.request.urlopen(B+subs[0],timeout=12).read().decode()
        else:
            sub=man
        segs=[l for l in sub.splitlines() if l.startswith('/proxy/seg')]
        if not segs: return (slug,'no-seg',None)
        r=urllib.request.urlopen(B+segs[0],timeout=15)
        data=r.read(16)
        if data.startswith(b'TSENCRY'):
            return (slug,'encrypted',None)
        return (slug,'ok',None)
    except Exception as e:
        return (slug,'err',str(e)[:40])

if __name__=='__main__':
    cat=json.load(open(CAT,encoding='utf-8'))
    print(f'[*] Escaneando {len(cat)}...',flush=True)
    enc=[]; err=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
        futs={ex.submit(check,d):d for d in cat}
        for i,f in enumerate(concurrent.futures.as_completed(futs),1):
            slug,res,msg=f.result()
            if res=='encrypted': enc.append(slug)
            elif res=='err': err.append(slug)
            if i%100==0: print(f'  {i}/{len(cat)} | cifrados:{len(enc)} err:{len(err)}',flush=True)
    # marcar en catalogo
    encset=set(enc)
    for d in cat:
        d['encrypted']= d['slug'] in encset
    json.dump(cat, open(CAT,'w',encoding='utf-8'), indent=2, ensure_ascii=False)
    open(os.path.join(ROOT,'encrypted.txt'),'w',encoding='utf-8').write('\n'.join(enc))
    print(f'\n[FIN] Cifrados:{len(enc)} | Errores:{len(err)} | Total:{len(cat)}',flush=True)
