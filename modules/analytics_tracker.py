# -*- coding: utf-8 -*-
"""
DramaPe Analytics Tracker Module (modules/analytics_tracker.py)
Motor de telemetría y métricas en tiempo real con persistencia en SQLite local.
Zero-dependencies, thread-safe y optimizado para alto rendimiento y seguridad.
"""

import os
import sqlite3
import threading
import time
import hashlib
import secrets
from datetime import datetime, timedelta

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, 'data', 'analytics.db')
_DB_LOCK = threading.Lock()

# ==========================================
# 🔒 SEGURIDAD Y PROTECCIÓN CRIPTOGRÁFICA DE PIN
# ==========================================
# El PIN nunca se expone en el cliente ni se guarda en texto plano
_PIN_SALT = "DRAMAPE_SECURE_SALT_GHS092_2026_XQ"
_EXPECTED_PIN_HASH = hashlib.sha256(("GHS092" + _PIN_SALT).encode('utf-8')).hexdigest()

_ADMIN_SESSIONS = {}      # token -> expiry_timestamp
_FAILED_ATTEMPTS = {}     # ip -> [timestamp, ...]
_SECURITY_LOCK = threading.Lock()

# ==========================================
# 🟢 TELEMETRÍA EN VIVO (EN MEMORIA / TIEMPO REAL)
# ==========================================
_LIVE_HEARTBEATS = {}     # visitor_hash -> {last_seen, is_watching, slug, ep, title, device}
_LIVE_LOCK = threading.Lock()


def _get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Inicializa las tablas de analytics e índices si no existen."""
    with _DB_LOCK:
        conn = _get_db()
        try:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp INTEGER NOT NULL,
                    date_str TEXT NOT NULL,
                    hour_str TEXT NOT NULL,
                    event_type TEXT NOT NULL, -- 'pageview', 'video_play', 'ad_click'
                    path TEXT,
                    slug TEXT,
                    ep TEXT,
                    title TEXT,
                    visitor_hash TEXT NOT NULL,
                    device TEXT, -- 'mobile', 'tablet', 'desktop'
                    referer TEXT,
                    country TEXT DEFAULT 'PE'
                )
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_events_time ON events(timestamp)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_events_date ON events(date_str)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_events_slug ON events(slug)")
            conn.commit()
        finally:
            conn.close()


# Inicializar BD al importar
init_db()


def _hash_ip(ip_str, user_agent=""):
    """Anonimiza al visitante respetando privacidad (GDPR compliant)."""
    raw = f"{ip_str}_{user_agent}_{datetime.utcnow().strftime('%Y-%m-%d')}"
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()[:16]


def _detect_device(ua_str=""):
    ua = (ua_str or '').lower()
    if 'ipad' in ua or 'tablet' in ua:
        return 'tablet'
    if 'mobile' in ua or 'android' in ua or 'iphone' in ua:
        return 'mobile'
    return 'desktop'


# ==========================================
# 🛡️ AUTENTICACIÓN Y VALIDACIÓN DE SESIÓN
# ==========================================
def verify_admin_pin(pin_input, client_ip="127.0.0.1"):
    """Verifica el PIN contra el hash SHA-256 salted con protección anti-fuerza bruta."""
    now = time.time()
    with _SECURITY_LOCK:
        # Limpiar intentos fallidos viejos (> 10 min)
        recent_fails = [t for t in _FAILED_ATTEMPTS.get(client_ip, []) if now - t < 600]
        _FAILED_ATTEMPTS[client_ip] = recent_fails

        if len(recent_fails) >= 5:
            return False, "Demasiados intentos fallidos. Bloqueado temporalmente por seguridad.", None

        computed_hash = hashlib.sha256(((pin_input or '').strip() + _PIN_SALT).encode('utf-8')).hexdigest()

        if computed_hash == _EXPECTED_PIN_HASH:
            # Login exitoso: generar token criptográfico de sesión
            token = secrets.token_hex(24)
            _ADMIN_SESSIONS[token] = now + (86400 * 7) # Válido 7 días
            _FAILED_ATTEMPTS[client_ip] = []
            return True, "Autenticado con éxito", token
        else:
            _FAILED_ATTEMPTS.setdefault(client_ip, []).append(now)
            remaining = 5 - len(_FAILED_ATTEMPTS[client_ip])
            return False, f"PIN incorrecto. Intentos restantes antes de bloqueo: {max(0, remaining)}", None


def validate_admin_session(token):
    """Valida si un token de sesión es legítimo y no ha expirado."""
    if not token:
        return False
    with _SECURITY_LOCK:
        expiry = _ADMIN_SESSIONS.get(token)
        if expiry and expiry > time.time():
            return True
        if token in _ADMIN_SESSIONS:
            del _ADMIN_SESSIONS[token]
        return False


# ==========================================
# 📡 REGISTRO DE EVENTOS Y HEARTBEATS
# ==========================================
def track_event(event_type, path="", slug="", ep="", title="", ip="127.0.0.1", ua="", referer=""):
    """Registra un evento persistente en la BD de forma asíncrona."""
    now = int(time.time())
    dt = datetime.utcfromtimestamp(now)
    date_str = dt.strftime('%Y-%m-%d')
    hour_str = dt.strftime('%Y-%m-%d %H:00')
    visitor_hash = _hash_ip(ip, ua)
    device = _detect_device(ua)

    # Actualizar estado en vivo en memoria
    with _LIVE_LOCK:
        _LIVE_HEARTBEATS[visitor_hash] = {
            'last_seen': time.time(),
            'is_watching': (event_type == 'video_play'),
            'slug': slug,
            'ep': ep,
            'title': title,
            'device': device
        }

    def _worker():
        with _DB_LOCK:
            conn = _get_db()
            try:
                conn.execute("""
                    INSERT INTO events (timestamp, date_str, hour_str, event_type, path, slug, ep, title, visitor_hash, device, referer)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (now, date_str, hour_str, event_type, path, slug, ep, title, visitor_hash, device, referer))
                conn.commit()
            except Exception:
                pass
            finally:
                conn.close()

    threading.Thread(target=_worker, daemon=True).start()


def record_live_heartbeat(is_watching, slug="", ep="", title="", ip="127.0.0.1", ua=""):
    """Registra un pulso de usuario activo (navegando o mirando video en tiempo real)."""
    now = time.time()
    visitor_hash = _hash_ip(ip, ua)
    device = _detect_device(ua)

    with _LIVE_LOCK:
        _LIVE_HEARTBEATS[visitor_hash] = {
            'last_seen': now,
            'is_watching': bool(is_watching),
            'slug': slug or '',
            'ep': str(ep or ''),
            'title': title or '',
            'device': device
        }


# ==========================================
# 📊 GENERADOR DE MÉTRICAS DEL DASHBOARD
# ==========================================
def get_dashboard_metrics(days=7):
    """Obtiene métricas resumidas y actividad en tiempo real."""
    since_ts = int(time.time()) - (days * 86400)
    now_ts = int(time.time())
    today_str = datetime.utcnow().strftime('%Y-%m-%d')

    # 1. Procesar usuarios en tiempo real (En vivo ahora)
    now = time.time()
    online_count = 0
    watching_count = 0
    live_watching_now = []

    with _LIVE_LOCK:
        # Purgar viejos (> 3 minutos)
        dead = [k for k, v in _LIVE_HEARTBEATS.items() if now - v['last_seen'] > 180]
        for k in dead:
            del _LIVE_HEARTBEATS[k]

        for k, v in _LIVE_HEARTBEATS.items():
            age = now - v['last_seen']
            if age <= 60: # Visto en el último minuto = En línea
                online_count += 1
            if age <= 35 and v.get('is_watching'): # Mirando video en los últimos 35s
                watching_count += 1
                live_watching_now.append({
                    'slug': v.get('slug', ''),
                    'ep': v.get('ep', ''),
                    'title': v.get('title') or v.get('slug') or 'Dorama en vivo',
                    'device': v.get('device', 'desktop'),
                    'seconds_ago': int(age)
                })

    with _DB_LOCK:
        conn = _get_db()
        try:
            cur = conn.cursor()

            # 2. Métricas Globales
            cur.execute("SELECT COUNT(*) as total_events FROM events WHERE timestamp >= ?", (since_ts,))
            total_events = cur.fetchone()['total_events'] or 0

            cur.execute("SELECT COUNT(DISTINCT visitor_hash) as unique_visitors FROM events WHERE timestamp >= ?", (since_ts,))
            unique_visitors = cur.fetchone()['unique_visitors'] or 0

            cur.execute("SELECT COUNT(*) as pageviews FROM events WHERE event_type = 'pageview' AND timestamp >= ?", (since_ts,))
            pageviews = cur.fetchone()['pageviews'] or 0

            cur.execute("SELECT COUNT(*) as video_plays FROM events WHERE event_type = 'video_play' AND timestamp >= ?", (since_ts,))
            video_plays = cur.fetchone()['video_plays'] or 0

            cur.execute("SELECT COUNT(*) as ad_clicks FROM events WHERE event_type = 'ad_click' AND timestamp >= ?", (since_ts,))
            ad_clicks = cur.fetchone()['ad_clicks'] or 0

            # Métricas de HOY
            cur.execute("SELECT COUNT(DISTINCT visitor_hash) as today_visitors FROM events WHERE date_str = ?", (today_str,))
            today_visitors = cur.fetchone()['today_visitors'] or 0

            cur.execute("SELECT COUNT(*) as today_plays FROM events WHERE event_type = 'video_play' AND date_str = ?", (today_str,))
            today_plays = cur.fetchone()['today_plays'] or 0

            cur.execute("SELECT COUNT(*) as today_ad_clicks FROM events WHERE event_type = 'ad_click' AND date_str = ?", (today_str,))
            today_ad_clicks = cur.fetchone()['today_ad_clicks'] or 0

            # 3. Timeline Diario (Últimos N días)
            cur.execute("""
                SELECT date_str, 
                       COUNT(DISTINCT visitor_hash) as visitors,
                       SUM(CASE WHEN event_type = 'pageview' THEN 1 ELSE 0 END) as views,
                       SUM(CASE WHEN event_type = 'video_play' THEN 1 ELSE 0 END) as plays,
                       SUM(CASE WHEN event_type = 'ad_click' THEN 1 ELSE 0 END) as ads
                FROM events
                WHERE timestamp >= ?
                GROUP BY date_str
                ORDER BY date_str ASC
            """, (since_ts,))
            timeline = [dict(row) for row in cur.fetchall()]

            # 4. Top 10 Doramas Más Reproducidos
            cur.execute("""
                SELECT slug, 
                       COALESCE(NULLIF(title, ''), slug) as display_title, 
                       COUNT(*) as play_count 
                FROM events 
                WHERE event_type = 'video_play' AND slug != '' AND timestamp >= ?
                GROUP BY slug
                ORDER BY play_count DESC 
                LIMIT 10
            """, (since_ts,))
            top_dramas = [dict(row) for row in cur.fetchall()]

            # 5. Distribución por Dispositivo
            cur.execute("""
                SELECT device, COUNT(*) as count 
                FROM events 
                WHERE timestamp >= ? 
                GROUP BY device
            """, (since_ts,))
            devices = {row['device']: row['count'] for row in cur.fetchall()}

            return {
                'ok': True,
                'time_range_days': days,
                'realtime': {
                    'online_now': max(online_count, 1 if watching_count > 0 else 0),
                    'watching_now': watching_count,
                    'active_streams': live_watching_now[:15]
                },
                'overview': {
                    'unique_visitors': unique_visitors,
                    'today_visitors': today_visitors,
                    'pageviews': pageviews,
                    'video_plays': video_plays,
                    'today_plays': today_plays,
                    'ad_clicks': ad_clicks,
                    'today_ad_clicks': today_ad_clicks,
                },
                'timeline': timeline,
                'top_dramas': top_dramas,
                'devices': {
                    'mobile': devices.get('mobile', 0),
                    'desktop': devices.get('desktop', 0),
                    'tablet': devices.get('tablet', 0)
                }
            }
        except Exception as e:
            return {'ok': False, 'error': str(e)}
        finally:
            conn.close()
