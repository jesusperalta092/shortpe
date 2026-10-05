# -*- coding: utf-8 -*-
"""
HotDrama Extractor - fuente: dramaboxdb.com (DramaBox)
--------------------------------------------------------
API descubierta (via __NEXT_DATA__):
  /api/trending                       -> catalogo
  /channel/trending|must-sees|hidden-gems  -> listados paginados
  /movie/{bookId}/{slug}              -> chapterList con m3u8Url/mp4 DIRECTORIOS (con firma)

Los m3u8Url tienen firma temporal (Expires) => se resuelven ON-DEMAND.
Salida: data/hotdrama.json
"""
import requests, json, os, sys, time, re, unicodedata

BASE = 'https://www.dramaboxdb.com'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
H = {'User-Agent': UA, 'Accept': 'text/html,*/*', 'Accept-Language': 'en-US,en;q=0.9', 'Referer': BASE + '/'}
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'data', 'hotdrama.json')

CHANNELS = ['/channel/trending', '/channel/must-sees', '/channel/hidden-gems']


def log(m):
    print(m); sys.stdout.flush()


def slugify(s):
    s = unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode()
    s = re.sub(r'[^a-zA-Z0-9]+', '-', s).strip('-').lower()
    return s[:60] or 'titulo'


def get_next_data(url):
    try:
        r = requests.get(url, headers=H, timeout=25)
        if r.status_code != 200:
            return None
        m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', r.text, re.S)
        if not m:
            return None
        return json.loads(m.group(1))['props']['pageProps']
    except Exception as e:
        log('  ERR %s: %s' % (url, str(e)[:60]))
        return None


def norm_item(it, seen):
    bid = it.get('bookId')
    if not bid or bid in seen:
        return None
    seen.add(bid)
    title = it.get('bookName') or it.get('bookNameEn') or ''
    return {
        'slug': 'hd-' + str(bid) + '-' + slugify(title),
        'title': title,
        'poster': it.get('cover') or '',
        'poster_local': '',
        'description': it.get('introduction') or '',
        'genres': it.get('tags') or it.get('labels') or [],
        'total_episodes': it.get('chapterCount') or 0,
        'episodes': {},
        'source': 'hotdrama',
        'section': 'hotdrama',
        'type': 'hls',
        'encrypted': False,
        'bookId': str(bid),
        'viewCount': it.get('viewCount') or 0,
        'author': it.get('author') or '',
    }


def main():
    out = []
    seen = set()
    # 1) Home (bigList)
    log('[HotDrama] Home...')
    pp = get_next_data(BASE + '/')
    if pp:
        for it in (pp.get('bigList') or []):
            n = norm_item(it, seen)
            if n: out.append(n)
    # 2) Canales (paginados)
    for ch in CHANNELS:
        page = 1
        while page <= 20:
            url = BASE + ch + ('?pageNo=%d' % page if page > 1 else '')
            log('  %s p%d' % (ch, page))
            pp = get_next_data(url)
            if not pp: break
            md = pp.get('moreData') or {}
            items = md.get('items') or []
            added = 0
            for it in items:
                n = norm_item(it, seen)
                if n: out.append(n); added += 1
            pages = pp.get('pages') or 1
            if page >= pages or added == 0:
                break
            page += 1
    # 3) Guardar
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False)
    log('[HotDrama] GUARDADO %d titulos en %s' % (len(out), OUT))


if __name__ == '__main__':
    main()
