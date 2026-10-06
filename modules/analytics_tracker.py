# -*- coding: utf-8 -*-
"""
DramaPe Analytics Tracker Module (modules/analytics_tracker.py)
Motor de telemetría y métricas de alta velocidad con persistencia en SQLite local.
Zero-dependencies, thread-safe y optimizado para alto rendimiento.
"""

import os
import sqlite3
import threading
import time
import hashlib
from datetime import datetime, timedelta

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, 'data', 'analytics.db')
_DB_LOCK = threading.Lock()

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

def track_event(event_type, path="", slug="", ep="", title="", ip="127.0.0.1", ua="", referer=""):
    """Registra un evento de forma asíncrona y segura."""
    now = int(time.time())
    dt = datetime.utcfromtimestamp(now)
    date_str = dt.strftime('%Y-%m-%d')
    hour_str = dt.strftime('%Y-%m-%d %H:00')
    visitor_hash = _hash_ip(ip, ua)
    device = _detect_device(ua)

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

def get_dashboard_metrics(days=7):
    """Obtiene métricas resumidas para el panel de administración."""
    since_ts = int(time.time()) - (days * 86400)
    now_ts = int(time.time())
    today_str = datetime.utcnow().strftime('%Y-%m-%d')

    with _DB_LOCK:
        conn = _get_db()
        try:
            cur = conn.cursor()

            # 1. Métricas Globales
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

            # 2. Timeline Diario (Últimos N días)
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

            # 3. Top 10 Doramas Más Reproducidos
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

            # 4. Distribución por Dispositivo
            cur.execute("""
                SELECT device, COUNT(*) as count 
                FROM events 
                WHERE timestamp >= ? 
                GROUP BY device
            """, (since_ts,))
            devices = {row['device']: row['count'] for row in cur.fetchall()}

            # 5. Actividad Reciente en Vivo (Últimos 15 minutos)
            live_cutoff = now_ts - 900
            cur.execute("SELECT COUNT(DISTINCT visitor_hash) as live_users FROM events WHERE timestamp >= ?", (live_cutoff,))
            live_users = cur.fetchone()['live_users'] or 0

            return {
                'ok': True,
                'time_range_days': days,
                'overview': {
                    'unique_visitors': unique_visitors,
                    'today_visitors': today_visitors,
                    'pageviews': pageviews,
                    'video_plays': video_plays,
                    'today_plays': today_plays,
                    'ad_clicks': ad_clicks,
                    'today_ad_clicks': today_ad_clicks,
                    'live_users': max(1, live_users)
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
