# -*- coding: utf-8 -*-
"""Para cada serie sin poster correcto, extrae SU poster desde su propia pagina."""
import requests, re, json, os, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed

UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36'
H={'User-Agent':UA,'Accept':'text/html,*/*','Referer':'https://dramaexpress.net/'}
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DT = os.path.join(ROOT,'data','dramatube.json')
STABLE = ('shorttv','farsun','mydramawave','dramabox','goodshort','crazymaple','netshort','toonshort','rivoshort','stardusttv','aurareeltv','yourwebnovel','cinerrashort','petadrama','vividshort','myluneshort','sixthshort','vyntagetv','allstarcluster','cloudfront','ihappyread','idrama','miraluneshort','dramawave','vigoo','alphashort')
BAD = ('1790247319_Gan2hDNR8e','cover-Os4BRoMS9Y')

def log(m):
    print(m); sys.stdout.flush()

def norm(s):
    return re.sub(r'[^a-z0-9]','', s.lower())

def get_poster_for(title, slug):
    """Busca el poster cuyo alt coincida con el titulo."""
    try:
        r = requests.get('https://dramaexpress.net/series/'+slug, headers=H, timeout=15)
        t = r.text.replace('\\/','/').replace('\\','')
        tgt = norm(title)
        cards = []
        for m in re.finditer(r'<img[^>]*alt="([^"]+)"[^>]*src="([^"]+)"', t):
            alt = m.group(1).strip()
            src = m.group(2).replace('&amp;','&')
            if not alt or not any(c in src for c in STABLE): continue
            if any(b in src for b in BAD): continue
            cards.append((norm(alt), src, alt))
        # 1) match exacto
        for nalt, src, alt in cards:
            if nalt == tgt:
                return src
        # 2) match parcial (uno contiene al otro)
        for nalt, src, alt in cards:
            if len(tgt)>6 and (tgt in nalt or nalt in tgt):
                return src
        return None
    except Exception:
        return None

d = json.load(open(DT, encoding='utf-8'))
# marcar los que tienen poster malo o duplicado
from collections import Counter
cnt = Counter(x.get('poster','') for x in d if x.get('poster'))
malos = [x for x in d if (not x.get('poster')) or cnt[x['poster']]>1 or any(b in x['poster'] for b in BAD)]
log('series con poster malo/duplicado: %d' % len(malos))

fixed=0
with ThreadPoolExecutor(max_workers=8) as ex:
    futs = {ex.submit(get_poster_for, x['title'], x['original_slug']): x for x in malos}
    done=0
    for fu in as_completed(futs):
        done+=1
        x = futs[fu]
        p = fu.result()
        if p:
            x['poster'] = p
            fixed += 1
        if done % 20 == 0:
            json.dump(d, open(DT,'w',encoding='utf-8'), ensure_ascii=False)
            log('  %d/%d | arreglados: %d' % (done, len(malos), fixed))

json.dump(d, open(DT,'w',encoding='utf-8'), ensure_ascii=False)
log('LISTO: %d arreglados de %d' % (fixed, len(malos)))
