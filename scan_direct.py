# -*- coding: utf-8 -*-
"""Scan de cifrados con Range header (evita cuelgues)"""
import json, os, sys, concurrent.futures, threading, socket
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

ROOT=r'C:\Users\USER\Downloads\Proyecto_Netflix_Dramas'
CAT=os.path.join(ROOT,'catalog_full.json')
UP='https://esdramia.com'
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36'
socket.setdefaulttimeout(8)

_tl = threading.local()
def sess():
    if not hasattr(_tl,'s'):
        s=requests.Session()
        s.mount('https://', HTTPAdapter(pool_connections=4, pool_maxsize=4, max_retries=Retry(total=0)))
        s.headers.update({'User-Agent':UA,'Referer':UP+'/'})
        _tl.s=s
    return _tl.s

ENCRYPTED=set(); ERRORS=set(); LOCK=threading.Lock()

def check(drama):
    slug=drama['slug']
    hashes=drama.get('episode_hashes') or {}
    if not hashes: return (slug,'no-ep')
    h=hashes.get('1') or list(hashes.values())[0]
    try:
        r=sess().get(f'{UP}/api/stream/{h}', timeout=8)
        obj=r.json()
        raw=obj['sources'][0]['url']
        full = raw if raw.startswith('http') else UP+raw
        low=full.split('?')[0].lower()
        if not (obj.get('type')=='hls' or low.endswith('s3hls') or low.endswith('.m3u8')):
            return (slug,'mp4')
        man=sess().get(full, timeout=8).text
        segs=[l.strip() for l in man.splitlines() if l.strip() and not l.startswith('#')]
        if not segs: return (slug,'no-seg')
        first=segs[0]
        full_seg = first if first.startswith('http') else (UP+first if first.startswith('/') else full.rsplit('/',1)[0]+'/'+first)
        # Range: solo 16 bytes
        rr=sess().get(full_seg, headers={'Range':'bytes=0-15'}, timeout=8)
        head=rr.content[:16]
        if head.startswith(b'TSENCRY'):
            with LOCK: ENCRYPTED.add(slug)
            return (slug,'encrypted')
        return (slug,'ok')
    except Exception as e:
        with LOCK: ERRORS.add(slug)
        return (slug,'err')

if __name__=='__main__':
    cat=json.load(open(CAT,encoding='utf-8'))
    print(f'[*] Escaneando {len(cat)} con Range+timeout8...',flush=True)
    done=0
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
        futs={ex.submit(check,d):d for d in cat}
        for f in concurrent.futures.as_completed(futs, timeout=None):
            done+=1
            if done%50==0: print(f'  {done}/{len(cat)} | cifrados:{len(ENCRYPTED)} err:{len(ERRORS)}',flush=True)
    for d in cat:
        d['encrypted']= d['slug'] in ENCRYPTED
    json.dump(cat, open(CAT,'w',encoding='utf-8'), indent=2, ensure_ascii=False)
    open(os.path.join(ROOT,'encrypted.txt'),'w',encoding='utf-8').write('\n'.join(sorted(ENCRYPTED)))
    print(f'\n[FIN] Cifrados:{len(ENCRYPTED)} Errores:{len(ERRORS)} Total:{len(cat)}',flush=True)
