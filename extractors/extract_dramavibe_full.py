# -*- coding: utf-8 -*-
"""
DramaVibe Full Extractor - chartdrama.com (catalogo completo)
--------------------------------------------------------------
Estrategia:
  1) Paginar /api/series?page=N&limit=100 para obtener TODO el catalogo (meta ligera)
  2) Para cada drama: /api/drama/{dramaId}/episodes -> {ep: url m3u8/mp4}
  3) Guardar solo los que tengan episodios. Checkpoint reanudable.

Salida: data/dramavibe.json  (formato compatible DramiaStream)
Checkpoint: data/dramavibe_ckpt.json
"""
import requests, json, os, sys, time, threading, re, unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = 'https://chartdrama.com'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
H = {'User-Agent': UA, 'Accept': 'application/json', 'Referer': BASE + '/'}
HL = {'User-Agent': UA, 'Accept': '*/*', 'Referer': BASE + '/'}
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'data', 'dramavibe.json')
CKPT = os.path.join(ROOT, 'data', 'dramavibe_ckpt.json')

_LOCK = threading.Lock()

def log(m):
    print(m); sys.stdout.flush()


def slugify(s):
    s = unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode()
    s = re.sub(r'[^a-zA-Z0-9]+', '-', s).strip('-').lower()
    return s[:60] or 'titulo'


def _get_page(page):
    try:
        r = requests.get(BASE + '/api/series?page=%d&limit=100' % page, headers=H, timeout=25)
        if r.status_code == 200:
            return r.json().get('items', [])
    except Exception:
        pass
    return None


def get_all_meta():
    """Pagina /api/series en PARALELO para traer TODO el catalogo."""
    # 1) pagina 1 para conocer el total
    r = requests.get(BASE + '/api/series?page=1&limit=100', headers=H, timeout=20)
    d = r.json()
    total = d.get('total', 0)
    limit = d.get('limit', 100) or 100
    pages = (total + limit - 1) // limit
    log('  catalogo: %d titulos, %d paginas (paralelo, workers=12)' % (total, pages))
    out = list(d.get('items', []))
    # 2) resto de paginas en paralelo
    done = [1]
    with ThreadPoolExecutor(max_workers=12) as ex:
        futs = {ex.submit(_get_page, p): p for p in range(2, pages + 1)}
        for fu in as_completed(futs):
            items = fu.result()
            if items:
                out.extend(items)
            done[0] += 1
            if done[0] % 40 == 0:
                log('  meta %d/%d paginas -> %d titulos' % (done[0], pages, len(out)))
    return out


def get_eps(drama_id):
    for attempt in range(2):
        try:
            r = requests.get(BASE + '/api/drama/%s/episodes' % drama_id, headers=H, timeout=12)
            if r.status_code == 200:
                return r.json().get('items', [])
            return []
        except Exception:
            time.sleep(0.4)
    return []


def load_ckpt():
    if os.path.exists(CKPT):
        try: return json.load(open(CKPT, encoding='utf-8'))
        except: pass
    return {'done_ids': [], 'items': [], 'meta': None}


def save_ckpt(ck):
    try:
        os.makedirs(os.path.dirname(CKPT), exist_ok=True)
        json.dump(ck, open(CKPT, 'w', encoding='utf-8'), ensure_ascii=False)
    except Exception: pass


def main():
    ck = load_ckpt()
    done = set(ck.get('done_ids', []))
    items = ck.get('items', [])
    log('[DramaVibe-FULL] checkpoint: %d procesados, %d con episodios' % (len(done), len(items)))

    # 1) meta
    if not ck.get('meta'):
        log('[1/2] Trayendo catalogo completo...')
        meta = get_all_meta()
        ck['meta'] = meta
        save_ckpt(ck)
        log('[1/2] %d titulos en catalogo' % len(meta))
    else:
        meta = ck['meta']
        log('[1/2] meta ya en checkpoint: %d titulos' % len(meta))

    # 2) episodios por drama
    log('[2/2] Procesando episodios (workers=8)...')
    pend = [m for m in meta if str(m.get('dramaId')) not in done]
    log('[2/2] pendientes: %d' % len(pend))
    cnt = [0]
    t0 = time.time()

    def work(m):
        did = m.get('dramaId')
        eps = get_eps(did)
        if not eps:
            return (did, None)
        ep_map = {}
        for e in eps:
            n = e.get('ep'); u = e.get('url')
            if n and u:
                ep_map[str(n)] = u if u.startswith('http') else (BASE + u)
        if not ep_map:
            return (did, None)
        title = m.get('title', '')
        slug = 'dv-%s-%s' % (did, slugify(title))
        item = {
            'slug': slug, 'title': title,
            'poster': m.get('cover', ''), 'poster_local': '',
            'description': m.get('synopsis', '') or m.get('description', ''),
            'genres': m.get('tags', []) or [],
            'total_episodes': len(ep_map),
            'episodes': ep_map,
            'source': 'dramavibe', 'section': 'dramavibe',
            'type': 'hls', 'encrypted': False,
            'sourceBookId': str(did),
            'playCount': m.get('playCount', 0),
            'latestEpisodeLabel': m.get('latestEpisodeLabel', ''),
        }
        return (did, item)

    with ThreadPoolExecutor(max_workers=16) as ex:
        futs = {ex.submit(work, m): m for m in pend}
        for fu in as_completed(futs):
            did, item = fu.result()
            done.add(str(did))
            if item: items.append(item)
            cnt[0] += 1
            if cnt[0] % 100 == 0:
                ck['done_ids'] = list(done); ck['items'] = items
                save_ckpt(ck)
                rate = cnt[0] / max(1, time.time() - t0)
                eta = (len(pend) - cnt[0]) / max(0.01, rate)
                log('  %d/%d | con-eps=%d | %.1f/s | ETA %.0fs' % (cnt[0], len(pend), len(items), rate, eta))

    # 3) guardar final
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(items, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False)
    ck['done_ids'] = list(done); ck['items'] = items
    save_ckpt(ck)
    log('[DramaVibe-FULL] LISTO: %d titulos con episodios guardados en %s' % (len(items), OUT))


if __name__ == '__main__':
    main()
