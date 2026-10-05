# -*- coding: utf-8 -*-
"""
DramaVibe Extractor - fuente: chartdrama.com
--------------------------------------------
API descubierta:
  GET /api/trending                    -> lista de dramas (rank, slug, title, cover, synopsis, tags, sourceBookId)
  GET /api/watch/{sourceBookId}        -> metadata + embedUrl (m3u8 del ep 1)
  GET /api/drama/{sourceBookId}/episodes -> {items:[{ep, url:/api/finddrama-hls/{id}/{ep}.m3u8}]}
  GET /api/finddrama-hls/{id}/{ep}.m3u8  -> HLS del episodio (segmentos proxied via workers.dev)

Salida: data/dramavibe.json (formato compatible con el catalogo de DramiaStream)
"""
import requests, json, os, sys, time

BASE = 'https://chartdrama.com'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
H = {'User-Agent': UA, 'Accept': 'application/json', 'Referer': BASE + '/'}
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'data', 'dramavibe.json')


def log(m):
    print(m); sys.stdout.flush()


def slugify(s):
    import re, unicodedata
    s = unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode()
    s = re.sub(r'[^a-zA-Z0-9]+', '-', s).strip('-').lower()
    return s or 'titulo'


def get_trending():
    r = requests.get(BASE + '/api/trending', headers=H, timeout=20)
    r.raise_for_status()
    return r.json().get('items', [])


def get_watch(sid):
    try:
        r = requests.get(BASE + '/api/watch/' + str(sid), headers=H, timeout=15)
        if r.status_code == 200: return r.json()
    except Exception as e:
        log('  watch/%s ERR %s' % (sid, str(e)[:60]))
    return None


def get_episodes(sid):
    try:
        r = requests.get(BASE + '/api/drama/' + str(sid) + '/episodes', headers=H, timeout=15)
        if r.status_code == 200:
            return r.json().get('items', [])
    except Exception as e:
        log('  episodes/%s ERR %s' % (sid, str(e)[:60]))
    return []


def build():
    log('[DramaVibe] Trayendo trending...')
    trending = get_trending()
    log('[DramaVibe] %d titulos en trending' % len(trending))
    out = []
    for i, it in enumerate(trending):
        sid = it.get('sourceBookId')
        title = it.get('title', '')
        if not sid:
            continue
        watch = get_watch(sid) or {}
        eps = get_episodes(sid)
        if not eps:
            log('  [%d/%d] %s -> SIN EPISODIOS, skip' % (i+1, len(trending), title[:30]))
            continue
        # episodes dict {ep: hls_url}
        ep_map = {}
        for e in eps:
            ep_num = e.get('ep')
            url = e.get('url')
            if ep_num and url:
                full = url if url.startswith('http') else (BASE + url)
                ep_map[str(ep_num)] = full
        slug = 'dv-' + str(sid) + '-' + slugify(title)
        item = {
            'slug': slug,
            'title': title,
            'poster': it.get('cover') or watch.get('cover', ''),
            'poster_local': '',
            'description': it.get('synopsis') or watch.get('synopsis', ''),
            'genres': it.get('tags') or watch.get('tags') or [],
            'total_episodes': len(ep_map),
            'episodes': ep_map,
            'source': 'dramavibe',
            'section': 'dramavibe',
            'type': 'hls',
            'encrypted': False,
            'sourceBookId': str(sid),
            'embedUrl': watch.get('embedUrl', ''),
        }
        out.append(item)
        log('  [%d/%d] %s -> %d eps' % (i+1, len(trending), title[:40], len(ep_map)))
        time.sleep(0.3)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    log('[DramaVibe] GUARDADO %d titulos en %s' % (len(out), OUT))
    return out


if __name__ == '__main__':
    build()
