# -*- coding: utf-8 -*-
"""
HotDrama Extractor - fuente: shortmax.org (ShortMax)
------------------------------------------------------
ShortMax ofrece TODO gratis (vipLocked=false). Los videos son .mp4 directos
con firma temporal => se resuelven ON-DEMAND.

Estructura en self.__next_f:
  - Series con subjectId, title, episodes[{se, ep, video.videoAddress.url, vipLocked}]

Salida: data/hotdrama.json
"""
import requests, json, os, sys, time, re, unicodedata

BASE = 'https://shortmax.org'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
H = {'User-Agent': UA, 'Accept': 'text/html,*/*', 'Accept-Language': 'en-US,en;q=0.9', 'Referer': BASE + '/'}
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'data', 'hotdrama.json')


def log(m):
    print(m); sys.stdout.flush()


def slugify(s):
    s = unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode()
    s = re.sub(r'[^a-zA-Z0-9]+', '-', s).strip('-').lower()
    return s[:60] or 'titulo'


def get_page(url):
    try:
        r = requests.get(url, headers=H, timeout=25)
        if r.status_code != 200:
            return ''
        t = r.text
        bl = re.findall(r'self\.__next_f\.push\(\[(\d+),"(.*?)"\]\)', t, re.S)
        at = ''
        for n, b in bl:
            try: at += b.encode().decode('unicode_escape', errors='ignore')
            except: at += b
        return at
    except Exception as e:
        log('  ERR %s: %s' % (url[:60], str(e)[:50]))
        return ''


def get_catalog():
    """Trae los enlaces /drama/... desde browse y home."""
    links = set()
    for page in ['/', '/browse']:
        try:
            r = requests.get(BASE + page, headers=H, timeout=25)
            # slugs con mayusculas/minusculas/guiones
            for m in re.findall(r'(/drama/[A-Za-z0-9_\-]+)', r.text):
                links.add(m)
        except Exception as e:
            log('  cat ERR %s: %s' % (page, str(e)[:50]))
    return list(links)


def parse_serie(url, link):
    # Primero el HTML crudo (para og:title y meta)
    raw = ''
    try:
        rr = requests.get(url, headers=H, timeout=25)
        raw = rr.text
    except Exception:
        raw = ''
    at = get_page(url)
    if not at:
        return None
    # titulo: preferir og:title (limpio) > title del objeto de serie
    title = ''
    mo = re.search(r'og:title" content="Watch ([^|]+?) Online Free', raw)
    if mo:
        title = mo.group(1).strip()
    if not title:
        mo2 = re.search(r'<title>Watch ([^|<]+)', raw)
        if mo2:
            title = mo2.group(1).strip()
    if not title:
        mt = re.search(r'"title":"([^"]{3,120})"', at)
        title = mt.group(1) if mt else ''
    # subjectId de la serie (el primero)
    ms = re.search(r'"subjectId":"(\d+)"', at)
    sid = ms.group(1) if ms else ''
    # cover: buscar la cover cuyo subjectId coincida (la de la serie)
    cover = ''
    if sid:
        mcv = re.search(r'"subjectId":"' + re.escape(sid) + r'".*?"cover":\{"url":"(https://[^"]+)"', at, re.S)
        if mcv: cover = mcv.group(1)
    if not cover:
        # fallback: og:image del HTML (el que tiene mas resolucion)
        mog = re.search(r'og:image" content="(https://[^"]+?)(?:\?|\")', raw)
        if mog:
            cover = mog.group(1)
    if not cover:
        mc = re.search(r'"cover":\{"url":"(https://[^"]+)"', at)
        cover = mc.group(1) if mc else ''
    # descripcion: la mas larga (la de la serie, no la de menu)
    desc = ''
    for md in re.finditer(r'"description":"([^"]{40,600})"', at):
        if len(md.group(1)) > len(desc):
            desc = md.group(1)
    # episodios: pares se/ep con url + vipLocked
    eps = {}
    pat = re.compile(r'"se":(\d+),"ep":(\d+),"video":\{"videoAddress":\{"url":"(https://[^"]+?)","duration":(\d+).*?"vipLocked":(true|false)', re.S)
    for m in pat.finditer(at):
        se, ep, vurl, dur, vip = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)
        if vip == 'true':
            continue  # salta bloqueados (no deberia haber)
        vurl = vurl.replace('\\u0026', '&').replace('\\/', '/')
        key = ep if se == '1' else ('%sx%s' % (se, ep))
        eps[key] = vurl
    if not eps:
        return None
    return {
        'slug': 'hd-' + (sid or slugify(title)) + '-' + slugify(title),
        'title': title,
        'poster': cover,
        'poster_local': '',
        'description': desc,
        'genres': [],
        'total_episodes': len(eps),
        'episodes': eps,
        'source': 'hotdrama',
        'section': 'hotdrama',
        'type': 'mp4',
        'encrypted': False,
        'subjectId': sid,
        'seoKey': link.rsplit('/', 1)[-1],
    }


def main():
    log('[ShortMax] Trayendo catalogo...')
    links = get_catalog()
    log('[ShortMax] %d enlaces encontrados' % len(links))
    out = []
    for i, link in enumerate(links):
        log('  [%d/%d] %s' % (i + 1, len(links), link[:60]))
        item = parse_serie(BASE + link, link)
        if item:
            out.append(item)
            log('     OK: %s (%d eps)' % (item['title'][:45], item['total_episodes']))
        time.sleep(0.3)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False)
    log('[ShortMax] GUARDADO %d series en %s' % (len(out), OUT))


if __name__ == '__main__':
    main()
