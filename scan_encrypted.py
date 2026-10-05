# -*- coding: utf-8 -*-
"""Detecta dramas con segmentos cifrados (TSENCRY_) y los marca en catalog_full.json"""
import urllib.request, json, os, concurrent.futures, sys, time

ROOT=r'C:\Users\USER\Downloads\Proyecto_Netflix_Dramas'
CAT=os.path.join(ROOT,'catalog_full.json')
B='http://127.0.0.1:8090'

def check(drama):
    slug=drama['slug']
    try:
        d=json.loads(urllib.request.urlopen(B+f'/proxy/episode?slug={slug}&ep=1',timeout=15).read())
        typ=d.get('player_type')
        if typ=='file':
            return (slug,'ok')
        man=urllib.request.urlopen(B+d['player_url'],timeout=15).read().decode()
        subs=[l for l in man.splitlines() if l.startswith('/proxy/manifest')]
        sub=urllib.request.urlopen(B+subs[0],timeout=15).read().decode() if subs else man
        segs=[l for l in sub.splitlines() if l.startswith('/proxy/seg')]
        if not segs: return (slug,'no-seg')
        data=urllib.request.urlopen(B+segs[0],timeout=20).read(16)
        if data.startswith(b'TSENCRY'): return (slug,'encrypted')
        return (slug,'ok')
    except Exception as e:
        return (slug,'err')

if __name__=='__main__':
    cat=json.load(open(CAT,encoding='utf-8'))
    print(f'[*] Escaneando {len(cat)} dramas...',flush=True)
    encrypted=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        futs={ex.submit(check,d):d for d in cat}
        for i,f in enumerate(concurrent.futures.as_completed(futs),1):
            slug,res=f.result()
            if res=='encrypted': encrypted.append(slug)
            if i%50==0: print(f'  {i}/{len(cat)} | cifrados: {len(encrypted)}',flush=True)
    # marcar en el catalogo
    for d in cat:
        d['encrypted']= d['slug'] in encrypted
    json.dump(cat, open(CAT,'w',encoding='utf-8'), indent=2, ensure_ascii=False)
    print(f'\n[FIN] Cifrados: {len(encrypted)} de {len(cat)}',flush=True)
    with open(os.path.join(ROOT,'encrypted.txt'),'w',encoding='utf-8') as f:
        f.write('\n'.join(encrypted))
