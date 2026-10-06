# -*- coding: utf-8 -*-
"""DramiaStream - Servidor v5 OPTIMIZADO: connection pooling + cache disco + streaming"""
import http.server, socketserver, urllib.parse, os, sys, mimetypes, re, json, threading, hashlib, time, unicodedata, hmac, base64
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from modules.analytics_tracker import (
    track_event, 
    get_dashboard_metrics, 
    verify_admin_pin, 
    validate_admin_session, 
    record_live_heartbeat
)

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

# Clave secreta interna para firma criptográfica de URLs y protección anti-scraping
_TOKEN_SECRET = b"dramia_elite_sec_key_2026_@#!"


def encode_url_token(real_url, ttl_seconds=86400):
    """Codifica y firma criptográficamente la URL real con HMAC-SHA256 y expiración."""
    if not real_url: return ""
    exp = int(time.time()) + ttl_seconds
    payload = f"{exp}|{real_url}".encode('utf-8')
    sig = hmac.new(_TOKEN_SECRET, payload, hashlib.sha256).digest()[:16]
    token_bytes = sig + payload
    return base64.urlsafe_b64encode(token_bytes).decode('ascii').rstrip('=')

def decode_url_token(token_str):
    """Decodifica el token, verifica la firma HMAC y valida que no esté vencido."""
    if not token_str: return None
    try:
        pad = len(token_str) % 4
        if pad: token_str += '=' * (4 - pad)
        raw = base64.urlsafe_b64decode(token_str.encode('ascii'))
        if len(raw) < 18: return None
        sig = raw[:16]
        payload = raw[16:]
        expected_sig = hmac.new(_TOKEN_SECRET, payload, hashlib.sha256).digest()[:16]
        if not hmac.compare_digest(sig, expected_sig):
            return None
        parts = payload.decode('utf-8', 'ignore').split('|', 1)
        if len(parts) != 2: return None
        exp, real_url = int(parts[0]), parts[1]
        if time.time() > exp + 86400:
            return None
        return real_url
    except Exception:
        return None

def resolve_requested_url(qs):
    """Resuelve la URL ya sea por token cifrado 't' o por parámetro 'url' (retrocompatible)."""
    token = qs.get('t', [''])[0]
    if token:
        real = decode_url_token(token)
        if real: return real
    up = qs.get('url', [''])[0]
    if up:
        if not up.startswith('http') and not up.startswith('/'):
            real = decode_url_token(up)
            if real: return real
        return up
    return ''

PORT = 8090
ROOT = os.path.dirname(os.path.abspath(__file__))
UPSTREAM = 'https://esdramia.com'
CACHE_DIR = os.path.join(ROOT, '_segcache')
os.makedirs(CACHE_DIR, exist_ok=True)

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
UP_HDRS = {'User-Agent': UA, 'Referer': UPSTREAM + '/', 'Accept': '*/*'}

# Session con pool de conexiones (clave para velocidad)
SESSION = requests.Session()
SESSION.verify = False
_adapter = HTTPAdapter(
    pool_connections=32, pool_maxsize=32, max_retries=Retry(total=2, backoff_factor=0.2),
)
SESSION.mount('https://', _adapter)
SESSION.mount('http://', _adapter)
SESSION.headers.update(UP_HDRS)

# BUILD_ID: se genera al arrancar, sirve para cache-busting
BUILD_ID = str(int(__import__('time').time()))

def _save_build_id():
    global BUILD_ID
    BUILD_ID=str(int(__import__('time').time()*1000))  # ms, siempre fresco
    try:
        open(os.path.join(ROOT,'BUILD_ID'),'w').write(BUILD_ID)
    except: pass
_save_build_id()
sys.stderr.write(f'[build] BUILD_ID={BUILD_ID}\n')

CATALOG = []
CAT_BY_SLUG = {}
CAT_LOCK = threading.Lock()
STREAM_CACHE = {}
STREAM_TTL = 180  # segundos antes de refrescar token dinamico
PREFETCHING = set()  # evita prefetch duplicado
ENC_CHECK = {}  # slug -> bool (True=encrypted)



# ============ LOGGER DETALLADO ============
import datetime as _dt
_LOG_DIR = os.path.join(ROOT, 'logs')
os.makedirs(_LOG_DIR, exist_ok=True)
_DETAIL_LOG = os.path.join(_LOG_DIR, 'server_detail.log')
_LOG_LOCK = threading.Lock()

def _dlog(tag, msg):
    try:
        ts = _dt.datetime.now().strftime('%H:%M:%S.%f')[:-3]
        with _LOG_LOCK:
            with open(_DETAIL_LOG, 'a', encoding='utf-8') as f:
                f.write('[%s][%s] %s\n' % (ts, tag, msg))
    except Exception: pass


def get_upstream_referer(url):
    """Devuelve el Referer adecuado según el dominio del recurso upstream para evitar 403 Forbidden."""
    if not url or not url.startswith('http'):
        return UPSTREAM + '/'
    try:
        host = urllib.parse.urlparse(url).netloc.lower()
        if 'toonory.com' in host: return 'https://toonory.com/'
        if 'chartdrama.com' in host or 'reelsshort' in host: return 'https://chartdrama.com/'
        if 'cukelis' in host: return 'https://cukelis.com/'
        if 'netshort' in host or 'nsstorage' in host or 'toonshort' in host: return 'https://netshort.com/'
        if 'vividshort' in host: return UPSTREAM + '/'
        if 'drama.tv' in host: return 'https://chartdrama.com/'
        if 'kalostv' in host: return 'https://kalostv.com/'
        if 'stardust-tv' in host: return 'https://stardust-tv.com/'
        if 'flextv' in host: return 'https://flextv.cc/'
        if 'shorttv' in host: return 'https://shorttv.live/'
        if 'mydramawave' in host: return 'https://mydramawave.com/'
        if 'shortswave' in host: return 'https://shortswave.com/'
        if 'dramaexpress' in host: return 'https://dramaexpress.net/'
        if any(h in host for h in ['dramabluff', 'serivibe', 'swoopreels', 'sanpplay', 'kynesttv', 'cinerratv', 'fliksotv', 'miraluneshort', 'cinerrashort', 'cinebytetv', 'blazeflick', 'pagejoytv', 'quickeltv', 'toptaletv', 'kaelixs', 'lumiloreqj', 'popmeloqj']):
            return 'https://dramaexpress.net/'
        if 'crazymaplestudios' in host: return 'https://crazymaplestudios.com/'
        if 'wolftv' in host: return 'https://wolftv.online/'
        if 'anyreel' in host: return 'https://anyreel.app/'
        if 'narto' in host or 'dramix' in host or 'nartodrama' in host: return 'https://dramix.tv/'
        if 'esdramia' in host: return 'https://esdramia.com/'
        parts = host.split('.')
        if len(parts) >= 2:
            return 'https://' + '.'.join(parts[-2:]) + '/'
        return 'https://' + host + '/'
    except Exception:
        return UPSTREAM + '/'


def get_upstream_headers(url, extra=None):
    """Genera cabeceras completas adaptadas al proveedor CDN del recurso."""
    hdrs = {
        'User-Agent': UA,
        'Referer': get_upstream_referer(url),
        'Accept': '*/*'
    }
    if extra:
        hdrs.update(extra)
    return hdrs


def _cache_manifest(url, text):
    try:
        mcp=cache_path('manifest_'+url)
        os.makedirs(os.path.dirname(mcp),exist_ok=True)
        open(mcp,'w',encoding='utf-8').write(text)
    except Exception: pass


def _abs(u, base, ref_url):
    if u.startswith('http'): return u
    if u.startswith('/'): return base+u
    return ref_url.rsplit('/',1)[0]+'/'+u


def _srt_to_vtt(srt_text):
    """Convierte subtitulos SRT a formato estandar WebVTT para navegadores y moviles."""
    if not srt_text: return 'WEBVTT\n\n'
    if srt_text.strip().startswith('WEBVTT'):
        return srt_text
    vtt = 'WEBVTT\n\n'
    lines = srt_text.replace('\r\n', '\n').split('\n')
    out = []
    for line in lines:
        if re.match(r'^\d{2}:\d{2}:\d{2},\d{3}\s+-->\s+\d{2}:\d{2}:\d{2},\d{3}', line.strip()):
            out.append(re.sub(r'(\d{2}:\d{2}:\d{2}),(\d{3})', r'\1.\2', line))
        else:
            out.append(line)
    return vtt + '\n'.join(out)


import threading as _th
_TLS = _th.local()

def _get_session():
    # Cada hilo tiene SU PROPIA Session (requests.Session NO es thread-safe)
    if not hasattr(_TLS, 'sess'):
        s = requests.Session()
        s.verify = False
        a = HTTPAdapter(pool_connections=4, pool_maxsize=4, max_retries=Retry(total=2, backoff_factor=0.3))
        s.mount('https://', a); s.mount('http://', a)
        s.headers.update(UP_HDRS)
        _TLS.sess = s
    return _TLS.sess

def _dl_one(full, hdrs):
    cp = cache_path(full)
    if os.path.exists(cp): return
    try:
        os.makedirs(os.path.dirname(cp), exist_ok=True)
        rr = requests.get(full, headers=hdrs, verify=False, timeout=(6, 15))
        if rr.status_code == 200 and len(rr.content) > 500:
            open(cp, 'wb').write(rr.content)
            try: open(cp + '.meta', 'w', encoding='utf-8').write(full)
            except: pass
    except Exception:
        pass


def _dl_segments(segs, base, hdrs, count=4):
    """Baja segmentos: primero sincrono, resto en paralelo con 2 workers (evita rate-limit del CDN)."""
    if not segs: return
    _dl_one(segs[0], hdrs)
    rest = segs[1:min(count, 4)]
    if rest:
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=2) as ex:
            list(ex.map(lambda s: _dl_one(s, hdrs), rest))


def prefetch_segments(slug, ep, count=3):
    """Warm cache: cachea el master + la calidad mas baja + primeros 3-4 segmentos."""
    count = min(count, 4)
    key=(slug,str(ep))
    if key in PREFETCHING: return
    PREFETCHING.add(key)
    try:
        _dlog('PREFETCH', 'START %s ep=%s' % (slug, ep))
        d = CAT_BY_SLUG.get(slug)
        if not d:
            _dlog('PREFETCH', 'NO CAT_BY_SLUG para %s' % slug)
            return
        src_name = d.get('source','esdramia')
        hdrs = {'User-Agent': UA, 'Accept': '*/*'}
        if src_name=='cukelis':
            eps_dict = d.get('episodes') or {}
            h = eps_dict.get(str(ep)) or (list(eps_dict.values())[0] if eps_dict else None)
            if not h: return
            man_url='https://cukelis.com/api/stream/'+h; base='https://cukelis.com'; hdrs['Referer']=base+'/'
        elif src_name=='narto':
            eps_dict = d.get('episodes') or {}
            man_url = eps_dict.get(str(ep)) or (list(eps_dict.values())[0] if eps_dict else None)
            if not man_url: return
            base='https://narto-drama.com'; hdrs['Referer']=base+'/'
        else:
            eps_dict = d.get('episode_hashes') or {}
            h = eps_dict.get(str(ep)) or (list(eps_dict.values())[0] if eps_dict else None)
            if not h: return
            try:
                api=requests.get(UPSTREAM+'/api/stream/'+h, headers={'User-Agent':UA,'Referer':UPSTREAM+'/','Accept':'application/json'}, verify=False, timeout=15).json()
                raw_u=api['sources'][0]['url']
                man_url=raw_u if raw_u.startswith('http') else UPSTREAM+raw_u
            except Exception: return
            base=UPSTREAM; hdrs['Referer']=base+'/'

        # 1) bajar y cachear el master
        _dlog('PREFETCH', 'man_url=%s' % man_url[:80])
        r=requests.get(man_url, headers=hdrs, verify=False, timeout=20)
        _dlog('PREFETCH', 'master status=%s len=%d' % (r.status_code, len(r.content)))
        raw=r.content.decode('utf-8','ignore')
        _cache_manifest(man_url, raw)
        lines=raw.splitlines()

        # 2) separar variantes (video) y audios
        variants=[]; audios=[]
        for ln in lines:
            s=ln.strip()
            if not s: continue
            if s.startswith('#EXT-X-MEDIA:') and 'URI=' in s:
                m=re.search(r'URI="([^"]+)"', s)
                if m: audios.append(m.group(1))
            elif not s.startswith('#'):
                variants.append(s)

        # 3) si NO hay variantes, es un sub-playlist directo: sus lineas son segmentos
        if not variants:
            segs=[]; last_base=man_url.rsplit('/',1)[0]
            for ln in lines:
                s=ln.strip()
                if s and not s.startswith('#'): segs.append(_abs(s, base, man_url))
            if segs: _dl_segments(segs, base, hdrs, count)
            return

        # 4) bajar SOLO la sub-playlist MAS BAJA (la que usa el player al arrancar) - rapido
        low_url, low_txt = None, None
        if variants:
            v = variants[-1]  # ultima = mas baja
            full = _abs(v, base, man_url)
            _is_m3u8 = (full.split('?')[0].lower().endswith('.m3u8')) or ('.m3u8' in full.lower()) or ('/api/stream/' in full)
            if _is_m3u8:
                try:
                    rr = requests.get(full, headers=hdrs, verify=False, timeout=15)
                    low_url = full
                    low_txt = rr.content.decode('utf-8','ignore')
                    _cache_manifest(full, low_txt)
                except Exception: pass

        # 5) cachear SOLO los primeros `count` segmentos (warmup rapido sin saturar conexion)
        if low_txt:
            segs = [_abs(l.strip(), base, low_url) for l in low_txt.splitlines() if l.strip() and not l.startswith('#')]
            segs = segs[:max(1, count)]
            _dlog('PREFETCH', '%s ep=%s WARMUP_SEGS=%d' % (slug, ep, len(segs)))
            mm = re.search(r'#EXT-X-MAP:URI="([^"]+)"', low_txt)
            if mm:
                _dl_segments([_abs(mm.group(1), base, low_url)], base, hdrs, 1)
            if segs:
                from concurrent.futures import ThreadPoolExecutor
                def _dl_log(s):
                    _dl_one(s, hdrs)
                with ThreadPoolExecutor(max_workers=2) as ex:
                    list(ex.map(_dl_log, segs))
                _dlog('PREFETCH', '%s ep=%s WARMUP OK %d segs' % (slug, ep, len(segs)))
    except Exception as e:
        _dlog('PREFETCH', 'ERROR %s' % str(e)[:200])
    finally:
        PREFETCHING.discard(key)



ENC_LOCK = threading.Lock()
ENCRYPTED_FILE = os.path.join(ROOT, 'encrypted.txt')


def is_encrypted(slug, manifest_url, is_hls):
    """Chequea si el primer segmento empieza con TSENCRY (cacheado). No bloquea si falla."""
    if not is_hls:
        return False
    with ENC_LOCK:
        if slug in ENC_CHECK:
            return ENC_CHECK[slug]
    try:
        hdrs = get_upstream_headers(manifest_url)
        man = requests.get(manifest_url, headers=hdrs, verify=False, timeout=12).text
        segs = [l.strip() for l in man.splitlines() if l.strip() and not l.startswith('#')]
        if not segs:
            with ENC_LOCK: ENC_CHECK[slug] = False
            return False
        first = segs[0]
        if first.startswith('http'): full = first
        elif first.startswith('/'): full = UPSTREAM + first
        else: full = manifest_url.rsplit('/',1)[0] + '/' + first
        hdrs_seg = get_upstream_headers(full, {'Range': 'bytes=0-15'})
        rr = requests.get(full, headers=hdrs_seg, verify=False, timeout=12)
        enc = rr.content[:16].startswith(b'TSENCRY')
        with ENC_LOCK: ENC_CHECK[slug] = enc
        return enc
    except Exception:
        with ENC_LOCK: ENC_CHECK[slug] = False
        return False


CAT_MTIMES = {}

def load_catalog(force=False):
    global CATALOG, CAT_BY_SLUG, CAT_MTIMES
    with CAT_LOCK:
        files = ('data/dramatube.json', 'catalog_full.json', 'catalog.json', 'data/narto.json', 'data/netshort.json', 'catalog_freereels.json')
        current_mtimes = {}
        needs_reload = force or not CATALOG
        for fname in files:
            p = os.path.join(ROOT, fname)
            if os.path.exists(p):
                mt = os.path.getmtime(p)
                current_mtimes[fname] = mt
                if CAT_MTIMES.get(fname) != mt:
                    needs_reload = True
        if not needs_reload:
            return
        CAT_MTIMES = current_mtimes

        all_items=[]
        # NOTA: dramavibe.json se carga APARTE (load_dramavibe) para no inflar el catalogo principal
        for fname in files:
            p=os.path.join(ROOT,fname)
            if os.path.exists(p):
                try:
                    data=json.load(open(p,encoding='utf-8'))
                    for d in data:
                        d.setdefault('section','drama')
                        d['section'] = d['section'].lower()
                        d.setdefault('source','esdramia')
                        if 'genres' in d and isinstance(d['genres'], list):
                            d['genres'] = list(dict.fromkeys(d['genres']))
                    if 'narto.json' in fname:
                        for d in data: d['source']='narto'
                    elif 'netshort.json' in fname:
                        for d in data: d['source']='netshort'
                    elif fname=='catalog_freereels.json':
                        for d in data: d['source']='freereels'
                    elif 'dramatube.json' in fname:
                        for d in data:
                            d['source']='dramatube'
                            d['section']='dramatube'
                    all_items.extend(data)
                    sys.stderr.write(f'[catalog] +{len(data)} de {fname}\n')
                except Exception as e:
                    sys.stderr.write(f'[catalog] err {fname}: {e}\n')
        all_items = [d for d in all_items if d.get('section') not in ('serie', 'pelicula')]
        # Ordenar para que los items con mas episodios/hashes queden primero al deduplicar
        def _ep_count(item):
            eps = item.get('episodes') or item.get('episode_hashes') or {}
            if isinstance(eps, dict): return len(eps)
            if isinstance(eps, list): return len(eps)
            return item.get('total_episodes') or 0
        all_items.sort(key=_ep_count, reverse=True)
        seen = set()
        seen_titles = set()
        uniq = []
        for d in all_items:
            s = d.get('slug')
            t = d.get('title') or ''
            raw_t = unicodedata.normalize('NFKD', t).encode('ascii', 'ignore').decode('utf-8').lower()
            nt = re.sub(r'\(dubbed\)|\[dubbed\]|\(espanol\)|\[espanol\]|\(es\)|\(doblado\)|\[doblado\]', '', raw_t)
            nt = re.sub(r'[^\w\s]', '', nt).strip()
            nt = re.sub(r'\s+', ' ', nt)
            if not s or s in seen:
                continue
            if nt and nt in seen_titles:
                continue
            seen.add(s)
            if nt:
                seen_titles.add(nt)
            uniq.append(d)
        CATALOG = uniq
        CAT_BY_SLUG = {d['slug']: d for d in CATALOG}
        sys.stderr.write(f'[catalog] TOTAL {len(CATALOG)} items (deduped)\n')
        return


# ============ DRAMAVIBE (catalogo grande, separado + paginado) ============
DV_ITEMS = []          # lista completa (lazy)
DV_BY_SLUG = {}        # slug -> item
DV_LOCK = threading.Lock()


def load_dramavibe():
    """Carga data/dramavibe.json UNA vez. Es grande (~52MB) por eso va aparte."""
    global DV_ITEMS, DV_BY_SLUG
    with DV_LOCK:
        if DV_ITEMS:
            return
        p = os.path.join(ROOT, 'data', 'dramavibe.json')
        if not os.path.exists(p):
            return
        try:
            data = json.load(open(p, encoding='utf-8'))
            for d in data:
                d['source'] = 'dramavibe'
                d['section'] = 'dramavibe'
            DV_ITEMS = data
            DV_BY_SLUG = {d['slug']: d for d in DV_ITEMS}
            sys.stderr.write('[dramavibe] cargados %d items\n' % len(DV_ITEMS))
        except Exception as e:
            sys.stderr.write('[dramavibe] err: %s\n' % e)


# ============ HOTDRAMA (dramaboxdb.com) ============
HD_ITEMS = []
HD_BY_SLUG = {}
HD_LOCK = threading.Lock()
HD_MTIME = 0
HD_CACHE = {}  # slug -> {t, episodes}
HD_TTL = 1800  # 30 min


def load_hotdrama(force=False):
    global HD_ITEMS, HD_BY_SLUG, HD_MTIME
    with HD_LOCK:
        p = os.path.join(ROOT, 'data', 'hotdrama.json')
        if not os.path.exists(p):
            return
        mt = os.path.getmtime(p)
        if not force and HD_ITEMS and HD_MTIME == mt:
            return
        HD_MTIME = mt
        try:
            data = json.load(open(p, encoding='utf-8'))
            for d in data:
                d.setdefault('source', 'hotdrama')
                d['section'] = 'hotdrama'
            HD_ITEMS = data
            HD_BY_SLUG = {d['slug']: d for d in HD_ITEMS}
            sys.stderr.write('[hotdrama] cargados %d items\n' % len(HD_ITEMS))
        except Exception as e:
            sys.stderr.write('[hotdrama] err: %s\n' % e)


def _hd_episodes(slug):
    """Resuelve episodios on-demand desde shortmax.org (mp4 con firma temporal, gratis)."""
    now = time.time()
    c = HD_CACHE.get(slug)
    if c and (now - c['t']) < HD_TTL:
        return c['eps']
    d = HD_BY_SLUG.get(slug)
    if not d:
        return {}
    seo = d.get('seoKey')
    # Si ya tenemos episodios pre-cargados y frescos, usarlos
    pre = d.get('episodes') or {}
    if not seo:
        return pre
    try:
        r = requests.get('https://shortmax.org/drama/' + str(seo),
                         headers={'User-Agent': UA, 'Accept': 'text/html,*/*', 'Referer': 'https://shortmax.org/'},
                         verify=False, timeout=20)
        if r.status_code != 200:
            return pre
        t = r.text
        bl = re.findall(r'self\.__next_f\.push\(\[(\d+),"(.*?)"\]\)', t, re.S)
        at = ''
        for n, b in bl:
            try: at += b.encode().decode('unicode_escape', errors='ignore')
            except: at += b
        eps = {}
        pat = re.compile(r'"se":(\d+),"ep":(\d+),"video":\{"videoAddress":\{"url":"(https://[^"]+?)","duration":(\d+).*?"vipLocked":(true|false)', re.S)
        for m in pat.finditer(at):
            se, ep, vurl, dur, vip = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)
            if vip == 'true':
                continue
            vurl = vurl.replace('\\u0026', '&').replace('\\/', '/')
            key = ep if se == '1' else ('%sx%s' % (se, ep))
            eps[key] = vurl
        if eps:
            HD_CACHE[slug] = {'t': now, 'eps': eps}
            return eps
    except Exception as e:
        _dlog('HD', 'episodes err %s: %s' % (slug, str(e)[:60]))
    return pre


def slugify_title(s):
    s = unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode()
    s = re.sub(r'[^a-zA-Z0-9]+', '-', s).strip('-').lower()
    return s


DV_CACHE = {}
DV_TTL = 900  # 15 minutos


def _dv_episodes(drama_id, source_book_id=None):
    """Resuelve episodios on-demand frescos con tokens validos desde chartdrama.com."""
    if not drama_id and not source_book_id:
        return {}
    key = str(drama_id or source_book_id)
    now = time.time()
    c = DV_CACHE.get(key)
    if c and (now - c['t']) < DV_TTL:
        return c['eps']

    # Si hay source_book_id, calentamos la sesion de chartdrama para firmar tokens S3 validos
    if source_book_id:
        try:
            requests.get('https://chartdrama.com/api/watch/' + urllib.parse.quote(str(source_book_id)),
                         headers={'User-Agent': UA, 'Accept': 'application/json', 'Referer': 'https://chartdrama.com/'},
                         verify=False, timeout=8)
        except Exception:
            pass

    try:
        r = requests.get(f'https://chartdrama.com/api/drama/{urllib.parse.quote(str(drama_id or source_book_id))}/episodes?_t={int(now*1000)}',
                         headers={'User-Agent': UA, 'Accept': 'application/json', 'Referer': 'https://chartdrama.com/', 'Cache-Control': 'no-cache'},
                         verify=False, timeout=12)
        if r.status_code == 200:
            items = r.json().get('items', [])
            out = {}
            for e in items:
                n = e.get('ep'); u = e.get('url')
                if n and u:
                    out[str(n)] = u if u.startswith('http') else ('https://chartdrama.com' + u)
            if out:
                DV_CACHE[key] = {'t': now, 'eps': out}
                return out
    except Exception as e:
        _dlog('DV', 'episodes err %s: %s' % (drama_id, str(e)[:80]))
    return {}


def to_full(u, base_dir):
    if u.startswith('http'): return u
    # derivar origen del base_dir (puede ser esdramia O cukelis)
    m=re.match(r'(https?://[^/]+)', base_dir)
    origin=m.group(1) if m else UPSTREAM
    if u.startswith('/'): return origin + u
    return base_dir + '/' + u

def proxy_uri(full_url):
    path_only = full_url.split('?')[0].lower()
    tok = encode_url_token(full_url)
    if path_only.endswith('.m3u8'):
        return '/proxy/manifest?t=' + tok
    return '/proxy/seg?t=' + tok

def cache_path(url):
    h = hashlib.md5(url.encode()).hexdigest()
    return os.path.join(CACHE_DIR, h[:2], h)



def _stream_get(slug, key):
    """Devuelve la respuesta cacheada si es valida (dentro del TTL)."""
    c = STREAM_CACHE.get(slug)
    if not c: return None
    item = c.get(key)
    if not item: return None
    data, ts = item
    if time.time() - ts > STREAM_TTL:
        return None
    return data


def _stream_set(slug, key, data):
    if slug not in STREAM_CACHE: STREAM_CACHE[slug] = {}
    STREAM_CACHE[slug][key] = (data, time.time())


class Handler(http.server.SimpleHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'  # keep-alive
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)
    def log_message(self, fmt, *args):
        try:
            msg = fmt % args
            _dlog('HTTP', msg)
        except Exception: pass
    def _send(self, code, ctype, data, extra=None, cache_header='no-store'):
        if code >= 400:
            try:
                snippet = data.decode('utf-8', 'ignore')[:120] if data else ''
                _dlog('HTTP_ERR', f"{code} {self.path} -> {snippet}")
            except Exception: pass
        try:
            self.send_response(code)
            self.send_header('Content-Type', ctype)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Accept-Ranges', 'bytes')
            self.send_header('Cache-Control', cache_header)
            self.send_header('Content-Length', str(len(data)) if data is not None else '0')
            if extra:
                for k,v in extra.items(): self.send_header(k, str(v))
            self.end_headers()
            if data: self.wfile.write(data)
        except (ConnectionAbortedError, BrokenPipeError, ConnectionResetError):
            pass

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)

        # ============ MANIFEST (con cache en disco y tokens HMAC) ============
        if path == '/proxy/manifest':
            up = resolve_requested_url(qs)
            if not up: return self._send(400,'text/plain',b'missing or invalid security token')
            mcp = cache_path('manifest_'+up)
            raw = None
            if os.path.exists(mcp):
                try:
                    raw = open(mcp, encoding='utf-8').read()
                    if not raw or not raw.strip().startswith('#'):
                        raw = None
                        try: os.remove(mcp)
                        except: pass
                except: raw = None
            if raw is None:
                try:
                    hdrs = get_upstream_headers(up)
                    r = requests.get(up, headers=hdrs, verify=False, timeout=20)
                    text = r.content.decode('utf-8', 'ignore')
                    if r.status_code == 200 and text.strip().startswith('#'):
                        raw = text
                        try:
                            os.makedirs(os.path.dirname(mcp), exist_ok=True)
                            open(mcp, 'w', encoding='utf-8').write(raw)
                        except: pass
                    else:
                        _dlog('ERR', f"manifest invalid or upstream {r.status_code}: {up}")
                        return self._send(502, 'text/plain', ('manifest invalid or status: ' + str(r.status_code)).encode())
                except Exception as e:
                    return self._send(502, 'text/plain', ('manifest: ' + str(e)[:80]).encode())
            base_dir = up.rsplit('/',1)[0]
            out=[]
            for line in raw.splitlines():
                s=line.strip()
                if s and not s.startswith('#'):
                    out.append(proxy_uri(to_full(s, base_dir)))
                elif s.startswith('#EXT-X-MAP:'):
                    m=re.search(r'URI="([^"]+)"', s)
                    if m:
                        full=to_full(m.group(1), base_dir)
                        out.append(s.replace(m.group(1), '/proxy/seg?t=' + encode_url_token(full)))
                    else: out.append(line)
                elif s.startswith('#EXT-X-MEDIA:'):
                    m=re.search(r'URI="([^"]+)"', s)
                    if m:
                        full=to_full(m.group(1), base_dir)
                        out.append(s.replace(m.group(1), proxy_uri(full)))
                    else: out.append(line)
                else:
                    out.append(line)
            body='\n'.join(out).encode('utf-8')
            return self._send(200,'application/vnd.apple.mpegurl',body,cache_header='no-store')

        # ============ SEGMENTO (cache + streaming real + Range) ============
        if path == '/proxy/seg':
            up = resolve_requested_url(qs)
            if not up: return self._send(400,'text/plain',b'missing or invalid security token')
            cp = cache_path(up)
            rng = self.headers.get('Range')
            _m = re.search(r'seg-(\d+)-', up)
            _dlog('SEG', 'REQ seg=%s range=%s cache=%s' % (_m.group(1) if _m else '?', rng, os.path.exists(cp)))
            # Cache hit (sin Range o con Range soportado por cache completa)
            if os.path.exists(cp):
                try:
                    data=open(cp,'rb').read()
                    if rng and rng.startswith('bytes='):
                        m=re.match(r'bytes=(\d+)-(\d*)', rng)
                        if m:
                            a=int(m.group(1)); b=int(m.group(2)) if m.group(2) else len(data)-1
                            b=min(b,len(data)-1)
                            chunk=data[a:b+1]
                            self.send_response(206)
                            self.send_header('Content-Type','video/mp2t')
                            self.send_header('Content-Range', f'bytes {a}-{b}/{len(data)}')
                            self.send_header('Content-Length', str(len(chunk)))
                            self.send_header('Access-Control-Allow-Origin','*')
                            self.send_header('Accept-Ranges','bytes')
                            self.send_header('Cache-Control','public, max-age=86400')
                            self.end_headers()
                            self.wfile.write(chunk)
                            return
                    self.send_response(200)
                    self.send_header('Content-Type','video/mp2t')
                    self.send_header('Content-Length', str(len(data)))
                    self.send_header('Access-Control-Allow-Origin','*')
                    self.send_header('Accept-Ranges','bytes')
                    self.send_header('Cache-Control','public, max-age=86400')
                    self.end_headers()
                    self.wfile.write(data)
                    return
                except Exception: pass
            # Miss: STREAMING real (chunks) - arranca a reproducir de inmediato
            hdrs = get_upstream_headers(up)
            if rng: hdrs['Range'] = rng
            try:
                r = requests.get(up, headers=hdrs, verify=False, timeout=(6, 25), stream=True)
                if r.status_code >= 400:
                    _dlog('SEG_ERR', f"status {r.status_code} for {up[:80]}")
                    return self._send(r.status_code, 'text/plain', (f'upstream {r.status_code}').encode())
            except Exception as e:
                _dlog('SEG_ERR', f"fetch error {e} for {up[:80]}")
                return self._send(502, 'text/plain', ('seg: ' + str(e)[:60]).encode())

            status = r.status_code
            ct = r.headers.get('Content-Type', 'video/mp2t')
            fh = None
            tmp_part = cp + '.part'
            if (not rng) and status == 200:
                try:
                    os.makedirs(os.path.dirname(cp), exist_ok=True)
                    fh = open(tmp_part, 'wb')
                except Exception:
                    fh = None

            self.send_response(status)
            self.send_header('Content-Type', ct)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Accept-Ranges', 'bytes')
            self.send_header('Cache-Control', 'public, max-age=86400')
            if 'Content-Range' in r.headers: self.send_header('Content-Range', r.headers['Content-Range'])
            if 'Content-Length' in r.headers: self.send_header('Content-Length', r.headers['Content-Length'])
            self.end_headers()
            try:
                for chunk in r.iter_content(65536):
                    if chunk:
                        if fh:
                            try: fh.write(chunk)
                            except: pass
                        self.wfile.write(chunk)
                if fh:
                    fh.close()
                    fh = None
                    try: os.replace(tmp_part, cp)
                    except: pass
            except (ConnectionAbortedError, BrokenPipeError, ConnectionResetError):
                pass
            except Exception:
                pass
            finally:
                if fh:
                    try:
                        fh.close()
                        if os.path.exists(tmp_part): os.remove(tmp_part)
                    except: pass
                r.close()
            return

        # ============ MP4 ============
        if path == '/proxy/stream':
            up = resolve_requested_url(qs)
            if not up: return self._send(400,'text/plain',b'missing or invalid security token')
            cp = cache_path('mp4_' + up)
            ctype = 'video/mp4'
            if os.path.exists(cp):
                try:
                    total = os.path.getsize(cp)
                    rng = self.headers.get('Range')
                    start, end = 0, total - 1
                    if rng and rng.startswith('bytes='):
                        spec = rng.split('=',1)[1].split(',')[0].strip()
                        if '-' in spec:
                            a, b = spec.split('-', 1)
                            if a: start = int(a)
                            if b: end = int(b)
                        if start < 0: start = 0
                        if end >= total: end = total - 1
                        if start > end: start = 0
                    length = end - start + 1
                    code = 206 if (rng and (start > 0 or end < total - 1) or rng) else 200
                    self.send_response(code)
                    self.send_header('Content-Type', ctype)
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Accept-Ranges', 'bytes')
                    self.send_header('Cache-Control', 'public, max-age=3600')
                    self.send_header('Content-Length', str(length))
                    if code == 206:
                        self.send_header('Content-Range', 'bytes %d-%d/%d' % (start, end, total))
                    self.end_headers()
                    with open(cp, 'rb') as fh:
                        fh.seek(start)
                        remaining = length
                        while remaining > 0:
                            blk = fh.read(min(262144, remaining))
                            if not blk: break
                            self.wfile.write(blk)
                            remaining -= len(blk)
                except (ConnectionAbortedError, BrokenPipeError, ConnectionResetError):
                    pass
                return

            # Si no esta en disco, STREAM DIRECTO CON RANGE (inicio instantaneo sin colgar el player)
            try:
                hdrs = get_upstream_headers(up)
                rng = self.headers.get('Range')
                if rng: hdrs['Range'] = rng
                r = requests.get(up, headers=hdrs, verify=False, timeout=(6, 30), stream=True)
                code = r.status_code
                if code >= 400:
                    return self._send(code, 'text/plain', (f'upstream {code}').encode())
                ct = r.headers.get('Content-Type', ctype)
                self.send_response(code)
                self.send_header('Content-Type', ct)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Accept-Ranges', 'bytes')
                self.send_header('Cache-Control', 'public, max-age=3600')
                if 'Content-Range' in r.headers:
                    self.send_header('Content-Range', r.headers['Content-Range'])
                if 'Content-Length' in r.headers:
                    self.send_header('Content-Length', r.headers['Content-Length'])
                self.end_headers()
                for chunk in r.iter_content(chunk_size=131072):
                    if chunk:
                        self.wfile.write(chunk)
            except (ConnectionAbortedError, BrokenPipeError, ConnectionResetError):
                pass
            except Exception as e:
                _dlog('ERR', f"mp4 stream error: {e}")
                return self._send(502, 'text/plain', ('stream: ' + str(e)[:80]).encode())
            return

        # ============ IMAGEN (cache en disco) ============
        if path == '/proxy/img':
            up = resolve_requested_url(qs)
            if not up: return self._send(400,'text/plain',b'missing or invalid security token')
            cp = cache_path('img_'+up)
            if os.path.exists(cp):
                return self._send(200,'image/webp',open(cp,'rb').read(),cache_header='public, max-age=604800')
            try:
                hdrs = get_upstream_headers(up, {'Accept': 'image/*,*/*'})
                r = requests.get(up, headers=hdrs, verify=False, timeout=25)
                data = r.content
                ctype = r.headers.get('Content-Type','image/webp')
                # Si el upstream dio error (403/404) intentar con referers alternativos conocidos
                if r.status_code != 200 or 'html' in ctype or len(data) < 500:
                    for fb_ref in ['https://dramaexpress.net/', 'https://' + urllib.parse.urlparse(up).netloc + '/', 'https://akamai-static.shorttv.live/', 'https://chartdrama.com/']:
                        try:
                            r2 = requests.get(up, headers={'User-Agent': UA, 'Referer': fb_ref, 'Accept': 'image/*,*/*'}, verify=False, timeout=8)
                            if r2.status_code == 200 and len(r2.content) >= 500:
                                r = r2
                                data = r.content
                                ctype = r.headers.get('Content-Type', 'image/webp')
                                break
                        except Exception: pass
                if r.status_code != 200 or 'html' in ctype or len(data) < 500:
                    return self._send(502,'text/plain',('img upstream %s' % r.status_code).encode())
                try:
                    os.makedirs(os.path.dirname(cp), exist_ok=True)
                    open(cp,'wb').write(data)
                except: pass
                return self._send(200, ctype, data, cache_header='public, max-age=604800')
            except Exception as e:
                return self._send(502,'text/plain',('img: '+str(e)[:80]).encode())

        # ============ SUBTÍTULOS (con conversión SRT -> WebVTT y cache en disco) ============
        if path == '/proxy/sub':
            up = resolve_requested_url(qs)
            if not up: return self._send(400,'text/plain',b'missing or invalid security token')
            cp = cache_path('sub_' + up)
            if os.path.exists(cp):
                try:
                    data = open(cp, 'rb').read()
                    return self._send(200, 'text/vtt; charset=utf-8', data, cache_header='public, max-age=86400')
                except: pass
            try:
                hdrs = get_upstream_headers(up, {'Accept': 'text/plain,*/*'})
                r = requests.get(up, headers=hdrs, verify=False, timeout=15)
                if r.status_code == 200 and r.text:
                    vtt = _srt_to_vtt(r.text).encode('utf-8')
                    try:
                        os.makedirs(os.path.dirname(cp), exist_ok=True)
                        open(cp, 'wb').write(vtt)
                    except: pass
                    return self._send(200, 'text/vtt; charset=utf-8', vtt, cache_header='public, max-age=86400')
                else:
                    return self._send(502, 'text/plain', ('sub upstream error: ' + str(r.status_code)).encode())
            except Exception as e:
                return self._send(502, 'text/plain', ('sub: ' + str(e)[:80]).encode())

        # ============ SUBTÍTULOS LOCALES (Español traducidos) ============
        if path == '/proxy/local-sub':
            slug = qs.get('slug', [''])[0]
            ep = qs.get('ep', ['1'])[0]
            lang = qs.get('lang', ['es'])[0]
            sub_file = os.path.join(ROOT, 'data', 'subtitles', slug, f"{ep}_{lang}.vtt")
            if os.path.exists(sub_file):
                try:
                    data = open(sub_file, 'rb').read()
                    return self._send(200, 'text/vtt; charset=utf-8', data, cache_header='public, max-age=86400')
                except Exception as e:
                    return self._send(500, 'text/plain', str(e).encode())
            return self._send(404, 'text/plain', b'subtitulo no encontrado')

        # ============ API STREAM ============
        if path == '/proxy/api':
            h = qs.get('hash',[''])[0]
            if not h: return self._send(400,'text/plain',b'missing hash')
            try:
                target_url = UPSTREAM+'/api/stream/'+urllib.parse.quote(h)
                hdrs = get_upstream_headers(target_url)
                r = requests.get(target_url, headers=hdrs, verify=False, timeout=20)
                return self._send(200,'application/json; charset=utf-8', r.content)
            except Exception as e:
                return self._send(502,'text/plain',('api: '+str(e)[:80]).encode())

                # ============ WARMUP (dispara prefetch sin esperar) ============
        if path == '/proxy/warmup':
            slug = qs.get('slug',[''])[0] or qs.get('id',[''])[0]
            if slug.startswith('cukelis-'): slug = slug[8:]
            ep = qs.get('ep',['1'])[0]
            if slug:
                threading.Thread(target=prefetch_segments, args=(slug,ep,4), daemon=True).start()
            return self._send(200,'application/json',b'{"ok":true}')

# ============ CUKELIS MANIFEST ============
        if path == '/proxy/cukelis-manifest':
            slug = qs.get('slug',[''])[0] or qs.get('id',[''])[0]
            if slug.startswith('cukelis-'): slug = slug[8:]
            ep = qs.get('ep',['1'])[0]
            d = CAT_BY_SLUG.get(slug)
            if not d: return self._send(404,'text/plain',b'no drama')
            eps_dict = d.get('episodes') or {}
            h = eps_dict.get(ep) or (list(eps_dict.values())[0] if eps_dict else None)
            if not h: return self._send(404,'text/plain',b'sin hash')
            try:
                _murl=f'https://cukelis.com/api/stream/{h}'
                _mcp=cache_path('manifest_'+_murl)
                raw=None
                if os.path.exists(_mcp):
                    try:
                        raw = open(_mcp, encoding='utf-8').read()
                        if not raw or not raw.strip().startswith('#'):
                            raw = None
                            try: os.remove(_mcp)
                            except: pass
                    except: raw = None
                if raw is None:
                    _hdrs = get_upstream_headers(_murl)
                    _r = requests.get(_murl, headers=_hdrs, verify=False, timeout=20)
                    text = _r.content.decode('utf-8', 'ignore')
                    if _r.status_code == 200 and text.strip().startswith('#'):
                        raw = text
                        try:
                            os.makedirs(os.path.dirname(_mcp), exist_ok=True)
                            open(_mcp, 'w', encoding='utf-8').write(raw)
                        except: pass
                    else:
                        _dlog('ERR', f"cukelis stream unavailable ({_r.status_code}): {_murl}")
                        return self._send(502, 'text/plain', b'cukelis: stream no disponible en origen')
                base='https://cukelis.com'
                out=[]
                for line in raw.splitlines():
                    s=line.strip()
                    if s and not s.startswith('#'):
                        full = s if s.startswith('http') else (base+s if s.startswith('/') else base+'/'+s)
                        out.append('/proxy/manifest?t=' + encode_url_token(full))
                    elif s.startswith('#EXT-X-MAP:'):
                        mm=re.search(r'URI="([^"]+)"', s)
                        if mm:
                            fu=mm.group(1)
                            full=fu if fu.startswith('http') else (base+fu if fu.startswith('/') else base+'/'+fu)
                            out.append(s.replace(fu, '/proxy/seg?t=' + encode_url_token(full)))
                        else: out.append(line)
                    elif s.startswith('#EXT-X-MEDIA:'):
                        mm=re.search(r'URI="([^"]+)"', s)
                        if mm:
                            fu=mm.group(1)
                            full=fu if fu.startswith('http') else (base+fu if fu.startswith('/') else base+'/'+fu)
                            out.append(s.replace(fu, '/proxy/manifest?t=' + encode_url_token(full)))
                        else: out.append(line)
                    else: out.append(line)
                return self._send(200,'application/vnd.apple.mpegurl','\n'.join(out).encode('utf-8'))
            except Exception as e:
                return self._send(502,'text/plain',('cukelis: '+str(e)[:80]).encode())

        # ============ EPISODIO ============
        if path == '/proxy/episode':
            slug = qs.get('slug',[''])[0] or qs.get('id',[''])[0]
            if slug.startswith('cukelis-'): slug = slug[8:]
            ep = qs.get('ep',['1'])[0]
            fresh = (qs.get('fresh',['0'])[0] == '1') or (qs.get('nocache',['0'])[0] == '1')
            if not slug: return self._send(400,'text/plain',b'missing slug')

            if not fresh:
                _c = _stream_get(slug, ep)
                if _c:
                    return self._send(200,'application/json; charset=utf-8', _c)


            # ===== DRAMAVIBE (busca aparte por su catalogo grande) =====
            if slug.startswith('dv-'):
                load_dramavibe()
                dv = DV_BY_SLUG.get(slug)
                if not dv: return self._send(404,'text/plain',b'no encontrado')
                d_id = dv.get('dramaId') or dv.get('sourceBookId') or dv.get('id')
                if not d_id:
                    m = re.search(r'dv-(\d+)-', slug)
                    if m: d_id = m.group(1)
                sb_id = dv.get('sourceBookId') or ''
                # Priorizar resolucion fresca on-demand para evitar enlaces S3 vencidos
                eps_dict = _dv_episodes(d_id or '', sb_id)
                if not eps_dict:
                    eps_dict = dv.get('episodes') or {}
                vurl = eps_dict.get(str(ep)) or (list(eps_dict.values())[0] if eps_dict else None)
                if not vurl: return self._send(404,'text/plain',b'sin episodio')
                is_hls = vurl.split('?')[0].lower().endswith('.m3u8')
                if is_hls:
                    obj={'title':dv.get('title',''),'type':'hls','player_type':'hls',
                         'player_url':'/proxy/manifest?t=' + encode_url_token(vurl),
                         'encrypted':False,'episode_number':str(ep)}
                else:
                    obj={'title':dv.get('title',''),'type':'mp4','player_type':'file',
                         'player_url':'/proxy/stream?t=' + encode_url_token(vurl),
                         'encrypted':False,'episode_number':str(ep)}
                out=json.dumps(obj,ensure_ascii=False).encode('utf-8')
                _stream_set(slug, ep, out)
                return self._send(200,'application/json; charset=utf-8',out)

            # ===== HOTDRAMA (dramaboxdb) =====
            if slug.startswith('hd-'):
                load_hotdrama()
                hd = HD_BY_SLUG.get(slug)
                if not hd: return self._send(404,'text/plain',b'no encontrado')
                eps_dict = _hd_episodes(slug)
                vurl = eps_dict.get(str(ep)) or (list(eps_dict.values())[0] if eps_dict else None)
                if not vurl: return self._send(404,'text/plain',b'sin episodio')
                is_hls = vurl.split('?')[0].lower().endswith('.m3u8')
                if is_hls:
                    obj={'title':hd.get('title',''),'type':'hls','player_type':'hls',
                         'player_url':'/proxy/manifest?t=' + encode_url_token(vurl),
                         'encrypted':False,'episode_number':str(ep)}
                else:
                    obj={'title':hd.get('title',''),'type':'mp4','player_type':'file',
                         'player_url':'/proxy/stream?t=' + encode_url_token(vurl),
                         'encrypted':False,'episode_number':str(ep)}
                out=json.dumps(obj,ensure_ascii=False).encode('utf-8')
                _stream_set(slug, ep, out)
                return self._send(200,'application/json; charset=utf-8',out)

            # Detectar fuente (cukelis no usa int)
            _d = CAT_BY_SLUG.get(slug)
            if _d and _d.get('source')=='cukelis':
                eps_dict = _d.get('episodes') or {}
                h = eps_dict.get(ep) or (list(eps_dict.values())[0] if eps_dict else None)
                if not h: return self._send(404,'text/plain',b'sin hash')
                obj={'hash':h,'title':_d.get('title',''),'type':'hls','player_type':'hls',
                     'player_url':'/proxy/cukelis-manifest?slug='+urllib.parse.quote(slug)+'&ep='+urllib.parse.quote(ep),
                     'encrypted':False}
                out=json.dumps(obj,ensure_ascii=False).encode('utf-8')
                _stream_set(slug, ep, out)
                # Prefetch en background de los primeros 4 segmentos (acelera el arranque)
                threading.Thread(target=prefetch_segments, args=(slug,ep,4), daemon=True).start()
                return self._send(200,'application/json; charset=utf-8',out)

            # ===== DRAMATUBE (DramaExpress HLS directo con subtitulos) =====
            if _d and _d.get('source')=='dramatube':
                eps_dict = _d.get('episodes') or {}
                m3u8 = eps_dict.get(str(ep)) or (list(eps_dict.values())[0] if eps_dict else None)
                if not m3u8: return self._send(404,'text/plain',b'sin m3u8')
                
                subs_dict = (_d.get('subtitles') or {}).get(str(ep)) or {}
                sub_list = []
                
                # 1. Verificar subtítulo en Español traducido localmente
                local_es_file = os.path.join(ROOT, 'data', 'subtitles', slug, f"{ep}_es.vtt")
                if os.path.exists(local_es_file):
                    sub_list.append({
                        'lang': 'es',
                        'label': 'Español',
                        'url': f'/proxy/local-sub?slug={urllib.parse.quote(slug)}&ep={urllib.parse.quote(str(ep))}&lang=es',
                        'default': True
                    })
                elif subs_dict.get('es'):
                    es_info = subs_dict.get('es')
                    url_es = es_info.get('url') if isinstance(es_info, dict) else es_info
                    sub_list.append({
                        'lang': 'es',
                        'label': 'Español',
                        'url': '/proxy/sub?t=' + encode_url_token(url_es),
                        'default': True
                    })

                # 2. Subtítulo en Inglés (secundario)
                en_sub = subs_dict.get('en') or subs_dict.get('en-US')
                if en_sub:
                    url_en = en_sub.get('url') if isinstance(en_sub, dict) else en_sub
                    sub_list.append({
                        'lang': 'en',
                        'label': 'English',
                        'url': '/proxy/sub?t=' + encode_url_token(url_en),
                        'default': len(sub_list) == 0
                    })
                elif not sub_list:
                    for lk, sinfo in subs_dict.items():
                        url = sinfo.get('url') if isinstance(sinfo, dict) else sinfo
                        if url:
                            sub_list.append({
                                'lang': lk,
                                'label': 'English',
                                'url': '/proxy/sub?t=' + encode_url_token(url),
                                'default': True
                            })
                            break
                    
                is_hls = ('.m3u8' in m3u8.split('?')[0].lower()) or ('s3hls' in m3u8) or ('/api/stream/' in m3u8)
                p_type = 'hls' if is_hls else 'file'
                v_type = 'hls' if is_hls else 'mp4'
                p_url = ('/proxy/manifest?t=' if is_hls else '/proxy/stream?t=') + encode_url_token(m3u8)
                
                obj={'hash':'stream_token','title':_d.get('title',''),'type':v_type,'player_type':p_type,
                     'player_url': p_url,
                     'encrypted':False,'episode_number':str(ep),
                     'subtitles': sub_list}
                out=json.dumps(obj,ensure_ascii=False).encode('utf-8')
                _stream_set(slug, ep, out)
                if is_hls:
                    threading.Thread(target=prefetch_segments, args=(slug,ep,4), daemon=True).start()
                return self._send(200,'application/json; charset=utf-8',out)

            # ===== NARTO (DramaShorts / HotDrama) - HLS o MP4 directo =====
            if _d and _d.get('source')=='narto':
                eps_dict = _d.get('episodes') or {}
                vurl = eps_dict.get(str(ep)) or (list(eps_dict.values())[0] if eps_dict else None)
                if not vurl: return self._send(404,'text/plain',b'sin episodio')
                is_hls = ('.m3u8' in vurl.split('?')[0].lower()) or ('s3hls' in vurl) or ('/api/stream/' in vurl)
                p_type = 'hls' if is_hls else 'file'
                v_type = 'hls' if is_hls else 'mp4'
                p_url = ('/proxy/manifest?t=' if is_hls else '/proxy/stream?t=') + encode_url_token(vurl)
                obj={'hash':'stream_token','title':_d.get('title',''),'type':v_type,'player_type':p_type,
                     'player_url': p_url,
                     'encrypted':False,'episode_number':str(ep)}
                out=json.dumps(obj,ensure_ascii=False).encode('utf-8')
                _stream_set(slug, ep, out)
                if is_hls:
                    threading.Thread(target=prefetch_segments, args=(slug,ep,4), daemon=True).start()
                return self._send(200,'application/json; charset=utf-8',out)

            try: ep_i=int(ep)
            except: return self._send(400,'text/plain',b'bad ep')
            _c = _stream_get(slug, ep_i)
            if _c:
                return self._send(200,'application/json; charset=utf-8', _c)

            d = CAT_BY_SLUG.get(slug)
            if not d:
                return self._send(404,'text/plain',b'no encontrado')

            # ===== CUKELIS (series / peliculas) =====
            if d.get('source')=='cukelis':
                eps_dict = d.get('episodes') or {}
                h = eps_dict.get(ep) or (list(eps_dict.values())[0] if eps_dict else None)
                if not h: return self._send(404,'text/plain',b'sin hash')
                obj={'hash':h,'title':d.get('title',''),'type':'hls',
                     'player_type':'hls',
                     'player_url':'/proxy/cukelis-manifest?slug='+urllib.parse.quote(slug)+'&ep='+urllib.parse.quote(ep),
                     'encrypted':False}
                out=json.dumps(obj,ensure_ascii=False).encode('utf-8')
                _stream_set(slug, ep, out)
                return self._send(200,'application/json; charset=utf-8',out)

            # ===== FREEREELS (MP4 directo S3) =====
            if d.get('source')=='freereels':
                eps_list = d.get('episodes') or []
                target = None
                try: ep_int = int(ep)
                except: ep_int = 1
                for e in eps_list:
                    if e.get('number')==ep_int:
                        target = e
                        break
                if not target and eps_list:
                    target = eps_list[0]
                if not target:
                    return self._send(404,'text/plain',b'sin episodios')
                vurl = target.get('video_url','')
                if not vurl:
                    return self._send(404,'text/plain',b'video_url vacia')
                obj={'title':d.get('title',''),'type':'mp4','player_type':'file',
                     'player_url':'/proxy/stream?t=' + encode_url_token(vurl),
                     'encrypted':False,
                     'episode_number':target.get('number'),
                     'episode_title':target.get('title','')}
                out=json.dumps(obj,ensure_ascii=False).encode('utf-8')
                _stream_set(slug, ep, out)
                return self._send(200,'application/json; charset=utf-8',out)

            # ===== NARTO / DRAMIX (MP4 directo con firma) =====
            if d.get('source')=='narto' or slug.startswith('nt-'):
                eps_dict = d.get('episodes') or {}
                vurl = eps_dict.get(str(ep)) or (list(eps_dict.values())[0] if eps_dict else None)
                if not vurl: return self._send(404,'text/plain',b'sin episodio')
                obj={'title':d.get('title',''),'type':'mp4','player_type':'file',
                     'player_url':'/proxy/stream?t=' + encode_url_token(vurl),
                     'encrypted':False,
                     'episode_number':str(ep)}
                out=json.dumps(obj,ensure_ascii=False).encode('utf-8')
                _stream_set(slug, ep, out)
                return self._send(200,'application/json; charset=utf-8',out)

            # ===== DRAMAVIBE (chartdrama) - HLS/MP4 =====
            if d.get('source')=='dramavibe':
                d_id = d.get('dramaId') or d.get('sourceBookId') or d.get('id')
                sb_id = d.get('sourceBookId') or ''
                # Priorizar resolucion fresca on-demand
                eps_dict = _dv_episodes(d_id or '', sb_id)
                if not eps_dict:
                    eps_dict = d.get('episodes') or {}
                vurl = eps_dict.get(str(ep)) or (list(eps_dict.values())[0] if eps_dict else None)
                if not vurl: return self._send(404,'text/plain',b'sin episodio')
                is_hls = vurl.split('?')[0].lower().endswith('.m3u8')
                if is_hls:
                    obj={'title':d.get('title',''),'type':'hls','player_type':'hls',
                         'player_url':'/proxy/manifest?t=' + encode_url_token(vurl),
                         'encrypted':False,'episode_number':str(ep)}
                else:
                    obj={'title':d.get('title',''),'type':'mp4','player_type':'file',
                         'player_url':'/proxy/stream?t=' + encode_url_token(vurl),
                         'encrypted':False,'episode_number':str(ep)}
                out=json.dumps(obj,ensure_ascii=False).encode('utf-8')
                _stream_set(slug, ep, out)
                return self._send(200,'application/json; charset=utf-8',out)

            # ===== HOTDRAMA (dramaboxdb) - HLS directo =====
            if d.get('source')=='hotdrama':
                eps_dict = _hd_episodes(slug)
                vurl = eps_dict.get(str(ep)) or (list(eps_dict.values())[0] if eps_dict else None)
                if not vurl: return self._send(404,'text/plain',b'sin episodio')
                is_hls = vurl.split('?')[0].lower().endswith('.m3u8')
                if is_hls:
                    obj={'title':d.get('title',''),'type':'hls','player_type':'hls',
                         'player_url':'/proxy/manifest?t=' + encode_url_token(vurl),
                         'encrypted':False,'episode_number':str(ep)}
                else:
                    obj={'title':d.get('title',''),'type':'mp4','player_type':'file',
                         'player_url':'/proxy/stream?t=' + encode_url_token(vurl),
                         'encrypted':False,'episode_number':str(ep)}
                out=json.dumps(obj,ensure_ascii=False).encode('utf-8')
                _stream_set(slug, ep, out)
                return self._send(200,'application/json; charset=utf-8',out)

            # ===== ESDRAMIA (dramas) =====
            h = None
            if d.get('episode_hashes') and not fresh:
                h = d['episode_hashes'].get(str(ep_i))
            if not h:
                try:
                    ref_url = f'{UPSTREAM}/dramas/{slug}/{ep_i}'
                    hdrs = get_upstream_headers(ref_url)
                    html = requests.get(ref_url, headers=hdrs, verify=False, timeout=20).text
                except Exception as e:
                    return self._send(502,'text/plain',('page: '+str(e)[:80]).encode())
                eps={}
                for m in re.finditer(r'\\"hash\\":\\"([0-9a-f]{32})\\",\\"title\\":\\"[^\\"]*\\",\\"episodeNumber\\":(\d+)', html):
                    eps[int(m.group(2))]=m.group(1)
                if not eps:
                    for m in re.finditer(r'\\"hash\\":\\"([0-9a-f]{32})\\"', html):
                        eps[len(eps)+1]=m.group(1)
                h = eps.get(ep_i)
                if h and d.get('episode_hashes'):
                    d['episode_hashes'][str(ep_i)] = h
            if not h:
                return self._send(404,'text/plain',(f'ep {ep_i} no encontrado').encode())

            try:
                ep_ref = f'{UPSTREAM}/dramas/{slug}/{ep_i}'
                hdrs = get_upstream_headers(UPSTREAM + '/api/stream/' + h, {'Referer': ep_ref, 'Accept': '*/*'})
                r = requests.get(UPSTREAM + '/api/stream/' + h, headers=hdrs, verify=False, timeout=20)
                obj = {}
                if r.status_code == 200:
                    try: obj = json.loads(r.text)
                    except: obj = {}
                sources = obj.get('sources')
                if not sources or not isinstance(sources, list) or len(sources) == 0:
                    try:
                        time.sleep(0.3)
                        html = requests.get(ep_ref, headers=get_upstream_headers(ep_ref), verify=False, timeout=15).text
                        eps = {}
                        for m in re.finditer(r'\\"hash\\":\\"([0-9a-f]{32})\\",\\"title\\":\\"[^\\"]*\\",\\"episodeNumber\\":(\d+)', html):
                            eps[int(m.group(2))] = m.group(1)
                        if not eps:
                            for m in re.finditer(r'\\"hash\\":\\"([0-9a-f]{32})\\"', html):
                                eps[len(eps)+1] = m.group(1)
                        fresh_h = eps.get(ep_i)
                        if fresh_h:
                            h = fresh_h
                            if d.get('episode_hashes'):
                                d['episode_hashes'][str(ep_i)] = fresh_h
                            fresh_hdrs = get_upstream_headers(UPSTREAM + '/api/stream/' + h, {'Referer': ep_ref, 'Accept': '*/*'})
                            fr = requests.get(UPSTREAM + '/api/stream/' + h, headers=fresh_hdrs, verify=False, timeout=15)
                            if fr.status_code == 200:
                                obj = json.loads(fr.text)
                                sources = obj.get('sources')
                    except Exception:
                        pass
                if not sources or not isinstance(sources, list) or len(sources) == 0:
                    return self._send(502, 'text/plain', b'episodio sin fuentes disponibles')
                raw = sources[0]['url']
                full = raw if raw.startswith('http') else UPSTREAM+raw
                low = full.split('?')[0].lower()
                is_hls = (obj.get('type')=='hls') or low.endswith('.m3u8') or low.endswith('s3hls') or low.endswith('/hls')
                clean_obj = {
                    'title': obj.get('title', d.get('title', '')),
                    'type': 'hls' if is_hls else 'file',
                    'player_type': 'hls' if is_hls else 'file',
                    'player_url': ('/proxy/manifest?t=' + encode_url_token(full)) if is_hls else ('/proxy/stream?t=' + encode_url_token(full)),
                    'encrypted': is_encrypted(slug, full, is_hls)
                }
                out = json.dumps(clean_obj, ensure_ascii=False).encode('utf-8')
                _stream_set(slug, ep_i, out)
                return self._send(200,'application/json; charset=utf-8',out)

            except Exception as e:
                _dlog('ERR', f"episode error: {e}")
                return self._send(502,'text/plain',('stream: '+str(e)[:80]).encode())

        # ============ DRAMAVIBE (paginado, catalogo grande) ============
        if path == '/api/dramavibe':
            load_dramavibe()
            try: page = int(qs.get('page',['1'])[0])
            except: page = 1
            try: limit = int(qs.get('limit',['48'])[0])
            except: limit = 48
            limit = max(1, min(limit, 200))
            q = (qs.get('q',[''])[0] or '').strip().lower()
            src = DV_ITEMS
            if q:
                src = [d for d in src if q in (d.get('title','').lower())]
            total = len(src)
            start = (page-1)*limit
            chunk = src[start:start+limit]
            # version ligera: sin 'episodes' (el player los pide on-demand)
            slim = [{k:v for k,v in d.items() if k != 'episodes'} for d in chunk]
            body = {'items': slim, 'page': page, 'limit': limit, 'total': total, 'pages': (total+limit-1)//limit}
            return self._send(200,'application/json; charset=utf-8', json.dumps(body, ensure_ascii=False).encode('utf-8'), cache_header='no-store')

        if path == '/api/dramavibe/stats':
            load_dramavibe()
            info = {'total': len(DV_ITEMS)}
            return self._send(200,'application/json; charset=utf-8', json.dumps(info).encode())

        if path == '/api/dramavibe/item':
            load_dramavibe()
            slug = qs.get('slug',[''])[0]
            d = DV_BY_SLUG.get(slug)
            if not d:
                return self._send(404,'application/json; charset=utf-8', b'{"error":"not found"}')
            item = {k:v for k,v in d.items() if k != 'episodes'}
            # Enriquecer on-demand: descripcion + tags + cover desde /api/watch/{sourceBookId}
            if not item.get('description') or not item.get('genres'):
                try:
                    sb = d.get('sourceBookId') or ''
                    if sb:
                        wr = requests.get('https://chartdrama.com/api/watch/' + urllib.parse.quote(str(sb)),
                                          headers={'User-Agent': UA, 'Accept':'application/json', 'Referer':'https://chartdrama.com/'},
                                          verify=False, timeout=10)
                        if wr.status_code == 200:
                            w = wr.json()
                            if not item.get('description'): item['description'] = w.get('synopsis','') or ''
                            if not item.get('genres'): item['genres'] = w.get('tags',[]) or []
                            if not item.get('poster'): item['poster'] = w.get('cover','') or ''
                except Exception as e:
                    _dlog('DV', 'watch err %s: %s' % (slug, str(e)[:60]))
            total = d.get('total_episodes', 0)
            if not total:
                eps = _dv_episodes(d.get('dramaId') or d.get('sourceBookId') or '', d.get('sourceBookId') or '')
                total = len(eps)
            item['total_episodes'] = total
            return self._send(200,'application/json; charset=utf-8', json.dumps(item, ensure_ascii=False).encode('utf-8'), cache_header='no-store')

        # ============ HOTDRAMA (dramaboxdb, paginado) ============
        if path == '/api/hotdrama':
            load_hotdrama()
            try: page = int(qs.get('page',['1'])[0])
            except: page = 1
            try: limit = int(qs.get('limit',['48'])[0])
            except: limit = 48
            limit = max(1, min(limit, 200))
            q = (qs.get('q',[''])[0] or '').strip().lower()
            src = HD_ITEMS
            if q:
                src = [d for d in src if q in (d.get('title','').lower())]
            total = len(src)
            start = (page-1)*limit
            chunk = src[start:start+limit]
            slim = [{k:v for k,v in d.items() if k != 'episodes'} for d in chunk]
            body = {'items': slim, 'page': page, 'limit': limit, 'total': total, 'pages': (total+limit-1)//limit}
            return self._send(200,'application/json; charset=utf-8', json.dumps(body, ensure_ascii=False).encode('utf-8'), cache_header='no-store')

        if path == '/api/hotdrama/stats':
            load_hotdrama()
            return self._send(200,'application/json; charset=utf-8', json.dumps({'total': len(HD_ITEMS)}).encode())

        if path == '/api/hotdrama/item':
            load_hotdrama()
            slug = qs.get('slug',[''])[0]
            d = HD_BY_SLUG.get(slug)
            if not d:
                return self._send(404,'application/json; charset=utf-8', b'{"error":"not found"}')
            item = {k:v for k,v in d.items() if k != 'episodes'}
            eps = _hd_episodes(slug)
            item['total_episodes'] = len(eps) or item.get('total_episodes', 0)
            return self._send(200,'application/json; charset=utf-8', json.dumps(item, ensure_ascii=False).encode('utf-8'), cache_header='no-store')

        # ============ STATS / CATALOG / HTML ============
        if path == '/api/stats':
            load_catalog(); load_dramavibe(); load_hotdrama()
            info={'total_dramas':len(CATALOG),'total_episodes':sum(len(d.get('episode_hashes',{})) for d in CATALOG),'total_dramavibe':len(DV_ITEMS),'total_hotdrama':len(HD_ITEMS)}
            return self._send(200,'application/json; charset=utf-8', json.dumps(info).encode())
        if path == '/api/catalog':
            load_catalog()
            # Version LIGERA: sin listas pesadas de episodios/subtitulos (se cargan on-demand al abrir modal/play)
            slim=[{k:v for k,v in d.items() if k not in ('episode_hashes','episodes','subtitles')} for d in CATALOG]
            return self._send(200,'application/json; charset=utf-8', json.dumps(slim,ensure_ascii=False).encode('utf-8'), cache_header='no-store')
        if path == '/catalog.json':
            for fname in ('catalog_full.json','catalog.json'):
                p=os.path.join(ROOT,fname)
                if os.path.exists(p):
                    return self._send(200,'application/json; charset=utf-8', open(p,'rb').read())
            return self._send(404,'text/plain',b'no catalog')
        if path in ('/','/index.html'):
            try:
                data=open(os.path.join(ROOT,'index.html'),'rb').read()
                # Inyectar BUILD_ID (cache-busting)
                data=data.replace(b'__BUILD_ID__', BUILD_ID.encode())
                self.send_response(200)
                self.send_header('Content-Type','text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(data)))
                self.send_header('Cache-Control','no-store, no-cache, must-revalidate, max-age=0')
                self.send_header('Pragma','no-cache')
                self.send_header('Expires','0')
                self.send_header('ETag', BUILD_ID)  # cambia al reiniciar
                self.end_headers()
                self.wfile.write(data)
                return
            except Exception as e:
                return self._send(500,'text/plain',str(e).encode())

        # Endpoint de version (para auto-reload)
        if path == '/api/version':
            return self._send(200,'application/json; charset=utf-8', json.dumps({'build':BUILD_ID}).encode())

        # Sirve /posters/* con headers CORS y cache
        if path.startswith('/posters/'):
            fp=os.path.join(ROOT, path.lstrip('/').replace('/',os.sep))
            if os.path.exists(fp) and os.path.isfile(fp):
                try:
                    data=open(fp,'rb').read()
                    ct='image/webp' if fp.endswith('.webp') else ('image/png' if fp.endswith('.png') else ('image/jpeg' if fp.endswith(('.jpg','.jpeg')) else 'application/octet-stream'))
                    self.send_response(200)
                    self.send_header('Content-Type', ct)
                    self.send_header('Content-Length', str(len(data)))
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Cache-Control', 'public, max-age=86400')
                    self.end_headers()
                    self.wfile.write(data)
                except Exception as e:
                    return self._send(500,'text/plain',str(e).encode())

        # ============ FIRST-PARTY AD UNLOCK & CLOAKING ============
        if path == '/api/unlock':
            step = qs.get('step', ['1'])[0]
            slug = qs.get('slug', [''])[0]
            ep = qs.get('ep', ['1'])[0]
            
            ad_targets = [
                'https://asiafilm.org/4/422780c437bf41678b7ed041ce2360a0',  # 1. Adsterra
                'https://omg10.com/4/11963834',                              # 2. Monetag
                'https://asiafilm.org/4/422780c437bf41678b7ed041ce2360a0',  # 3. Adsterra
                'https://omg10.com/4/11963834'                               # 4. Monetag
            ]
            try:
                step_idx = (int(step) - 1) % len(ad_targets)
                if step_idx < 0: step_idx = 0
            except Exception:
                step_idx = 0
            
            target_ad = ad_targets[step_idx]
            ad_network = 'monetag' if ('omg10' in target_ad or 'monetag' in target_ad) else 'adsterra'
            
            try:
                client_ip = self.headers.get('CF-Connecting-IP') or self.headers.get('X-Forwarded-For', '').split(',')[0].strip() or self.client_address[0]
                user_agent = self.headers.get('User-Agent', '')
                track_event('ad_click', slug=slug, episode=ep, client_ip=client_ip, user_agent=user_agent, metadata={'step': step, 'network': ad_network})
            except Exception as e:
                _dlog('UNLOCK_ERR', f"analytics tracking failed: {e}")

            self.send_response(302)
            self.send_header('Location', target_ad)
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            return

        # ============ ANALYTICS DASHBOARD (PROTEGIDO POR SESIÓN CRIPTOGRÁFICA) ============
        if path == '/api/analytics/dashboard':
            auth_header = self.headers.get('Authorization', '')
            token = ''
            if auth_header.startswith('Bearer '):
                token = auth_header[7:].strip()
            if not token:
                token = qs.get('token', [''])[0]
            if not validate_admin_session(token):
                return self._send(401, 'application/json; charset=utf-8', b'{"ok":false,"error":"No autorizado. Requiere PIN"}', cache_header='no-store')

            try: days = int(qs.get('days', ['7'])[0])
            except: days = 7
            metrics = get_dashboard_metrics(days=days)
            body = json.dumps(metrics, ensure_ascii=False).encode('utf-8')
            return self._send(200, 'application/json; charset=utf-8', body, cache_header='no-store')

        # Sirve /lib/* con headers anti-cache (fuerza recarga al cambiar version)
        if path.startswith('/lib/'):
            fp=os.path.join(ROOT, path.lstrip('/').replace('/',os.sep))
            if os.path.exists(fp) and os.path.isfile(fp):
                try:
                    data=open(fp,'rb').read()
                    ct='application/javascript; charset=utf-8' if fp.endswith('.js') else ('text/css' if fp.endswith('.css') else 'application/octet-stream')
                    self.send_response(200)
                    self.send_header('Content-Type', ct)
                    self.send_header('Content-Length', str(len(data)))
                    self.send_header('Cache-Control','no-store, no-cache, must-revalidate, max-age=0')
                    self.send_header('Pragma','no-cache')
                    self.send_header('Expires','0')
                    self.end_headers()
                    self.wfile.write(data)
                    return
                except Exception as e:
                    return self._send(500,'text/plain',str(e).encode())

        try:
            return super().do_GET()
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError, ConnectionError):
            pass

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # 1. Login seguro de Admin (Verificación de PIN con SHA-256 + Salt)
        if path == '/api/analytics/auth':
            try:
                length = int(self.headers.get('Content-Length', 0))
                raw = self.rfile.read(length).decode('utf-8') if length > 0 else '{}'
                data = json.loads(raw)
                client_ip = self.headers.get('CF-Connecting-IP') or self.headers.get('X-Forwarded-For', '').split(',')[0].strip() or self.client_address[0]
                pin = data.get('pin', '')
                ok, msg, token = verify_admin_pin(pin, client_ip)
                if ok:
                    return self._send(200, 'application/json', json.dumps({'ok': True, 'token': token}).encode(), cache_header='no-store')
                else:
                    return self._send(401, 'application/json', json.dumps({'ok': False, 'error': msg}).encode(), cache_header='no-store')
            except Exception as e:
                return self._send(400, 'application/json', json.dumps({'ok': False, 'error': str(e)}).encode(), cache_header='no-store')

        # 2. Pulso en vivo (Heartbeat de usuarios y espectadores en tiempo real)
        if path == '/api/analytics/heartbeat':
            try:
                length = int(self.headers.get('Content-Length', 0))
                raw = self.rfile.read(length).decode('utf-8') if length > 0 else '{}'
                data = json.loads(raw)
                client_ip = self.headers.get('CF-Connecting-IP') or self.headers.get('X-Forwarded-For', '').split(',')[0].strip() or self.client_address[0]
                ua = self.headers.get('User-Agent', '')
                record_live_heartbeat(
                    is_watching=bool(data.get('is_watching', False)),
                    slug=data.get('slug', ''),
                    ep=str(data.get('ep', '')),
                    title=data.get('title', ''),
                    ip=client_ip,
                    ua=ua
                )
                return self._send(200, 'application/json', b'{"ok":true}', cache_header='no-store')
            except Exception as e:
                return self._send(400, 'application/json', json.dumps({'ok': False, 'error': str(e)}).encode(), cache_header='no-store')

        # 3. Registro de eventos (pageview, video_play, ad_click)
        if path == '/api/analytics/track':
            try:
                length = int(self.headers.get('Content-Length', 0))
                raw = self.rfile.read(length).decode('utf-8') if length > 0 else '{}'
                data = json.loads(raw)
                client_ip = self.headers.get('CF-Connecting-IP') or self.headers.get('X-Forwarded-For', '').split(',')[0].strip() or self.client_address[0]
                ua = self.headers.get('User-Agent', '')
                ref = self.headers.get('Referer', '')
                track_event(
                    event_type=data.get('event_type', 'pageview'),
                    path=data.get('path', ''),
                    slug=data.get('slug', ''),
                    ep=str(data.get('ep', '')),
                    title=data.get('title', ''),
                    ip=client_ip,
                    ua=ua,
                    referer=ref
                )
                return self._send(200, 'application/json', b'{"ok":true}', cache_header='no-store')
            except Exception as e:
                return self._send(400, 'application/json', json.dumps({'ok': False, 'error': str(e)}).encode(), cache_header='no-store')
        return self._send(404, 'text/plain', b'not found')

    def copyfile(self, source, outputfile):
        try:
            super().copyfile(source, outputfile)
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError, ConnectionError):
            pass

    def handle(self):
        try:
            super().handle()
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError, ConnectionError):
            pass


class ThreadingServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


if __name__ == '__main__':
    mimetypes.add_type('application/vnd.apple.mpegurl', '.m3u8')
    mimetypes.add_type('video/mp2t', '.ts')
    os.chdir(ROOT)
    load_catalog()
    print('\n  ========================================')
    print('   DramaPe Server v5 (optimizado) - http://localhost:'+str(PORT))
    print('  ========================================')
    print(f'   {len(CATALOG)} dramas | cache en _segcache/')
    print('  Ctrl+C para detener.\n')
    with ThreadingServer(('127.0.0.1',PORT), Handler) as httpd:
        try: httpd.serve_forever()
        except KeyboardInterrupt: print('\n  Detenido.\n')
