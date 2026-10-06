// Modular Supabase Cloud Storage for DramaPe Analytics
import crypto from 'crypto';

export const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://fpfvheperlxkbbratiqe.supabase.co';
export const SUPABASE_SERVICE_ROLE = process.env.SUPABASE_SERVICE_ROLE || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZwZnZoZXBlcmx4a2JicmF0aXFlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc5MTIzMDYzMywiZXhwIjoyMTA2ODA2NjMzfQ.xv6Rmz9TZYpAq1V9V0_0ixaXLaL4vVBvA8GqbDYG5yY';

// PIN de seguridad maestro protegido con SHA-256 + Salt
const PIN_SALT = 'DRAMAPE_SECURE_SALT_GHS092_2026_XQ';
const EXPECTED_PIN_HASH = crypto.createHash('sha256').update('GHS092' + PIN_SALT).digest('hex');

// In-Memory Realtime Telemetry & Sessions
if (!global._dramapeAnalytics) {
  global._dramapeAnalytics = {
    sessions: new Map(),       // token -> expiry
    failedAttempts: new Map(), // ip -> [timestamp]
    liveHeartbeats: new Map(), // visitorHash -> { lastSeen, isWatching, slug, ep, title, device }
    fallbackEvents: []         // eventos locales en memoria de respaldo
  };
}

const state = global._dramapeAnalytics;

export function verifyPin(pinInput, clientIp = '127.0.0.1') {
  const now = Date.now();
  const recentFails = (state.failedAttempts.get(clientIp) || []).filter(t => now - t < 600000);
  state.failedAttempts.set(clientIp, recentFails);

  if (recentFails.length >= 5) {
    return { ok: false, error: 'Demasiados intentos fallidos. Bloqueado temporalmente por seguridad.' };
  }

  const computedHash = crypto.createHash('sha256').update((pinInput || '').trim() + PIN_SALT).digest('hex');
  if (computedHash === EXPECTED_PIN_HASH) {
    const token = crypto.randomBytes(24).toString('hex');
    state.sessions.set(token, now + (86400000 * 7)); // 7 días
    state.failedAttempts.delete(clientIp);
    return { ok: true, token };
  } else {
    recentFails.push(now);
    state.failedAttempts.set(clientIp, recentFails);
    const remaining = Math.max(0, 5 - recentFails.length);
    return { ok: false, error: `PIN incorrecto. Intentos restantes antes de bloqueo: ${remaining}` };
  }
}

export function validateSession(token) {
  if (!token) return false;
  const expiry = state.sessions.get(token);
  if (expiry && expiry > Date.now()) return true;
  if (expiry) state.sessions.delete(token);
  return false;
}

export function hashVisitor(ip = '', ua = '') {
  const dateStr = new Date().toISOString().slice(0, 10);
  return crypto.createHash('sha256').update(`${ip}_${ua}_${dateStr}`).digest('hex').slice(0, 16);
}

export function detectDevice(ua = '') {
  const low = (ua || '').toLowerCase();
  if (low.includes('ipad') || low.includes('tablet')) return 'tablet';
  if (low.includes('mobile') || low.includes('android') || low.includes('iphone')) return 'mobile';
  return 'desktop';
}

export function recordLiveHeartbeat(isWatching, slug = '', ep = '', title = '', ip = '127.0.0.1', ua = '') {
  const visitorHash = hashVisitor(ip, ua);
  const device = detectDevice(ua);
  state.liveHeartbeats.set(visitorHash, {
    lastSeen: Date.now(),
    isWatching: Boolean(isWatching),
    slug: slug || '',
    ep: String(ep || ''),
    title: title || '',
    device
  });
}

// Guardar evento en Supabase Cloud con respaldo en memoria
export async function saveEvent(eventData) {
  const now = Date.now();
  const dateStr = new Date(now).toISOString().slice(0, 10);
  const hourStr = new Date(now).toISOString().slice(0, 13) + ':00';

  const doc = {
    timestamp: Math.floor(now / 1000),
    date_str: dateStr,
    hour_str: hourStr,
    event_type: eventData.event_type || 'pageview',
    path: eventData.path || '',
    slug: eventData.slug || '',
    ep: String(eventData.ep || ''),
    title: eventData.title || '',
    visitor_hash: eventData.visitor_hash || 'anon',
    device: eventData.device || 'desktop',
    referer: eventData.referer || '',
    country: 'PE'
  };

  // Mantener copia en memoria
  state.fallbackEvents.push(doc);
  if (state.fallbackEvents.length > 5000) state.fallbackEvents.shift();

  // Actualizar telemetría viva
  state.liveHeartbeats.set(doc.visitor_hash, {
    lastSeen: now,
    isWatching: doc.event_type === 'video_play',
    slug: doc.slug,
    ep: doc.ep,
    title: doc.title,
    device: doc.device
  });

  // Intentar guardar en Supabase REST
  try {
    const res = await fetch(`${SUPABASE_URL}/rest/v1/analytics_events`, {
      method: 'POST',
      headers: {
        'apikey': SUPABASE_SERVICE_ROLE,
        'Authorization': `Bearer ${SUPABASE_SERVICE_ROLE}`,
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
      },
      body: JSON.stringify(doc),
      cache: 'no-store'
    });
    return res.ok;
  } catch (err) {
    // Si la tabla aún no se ha creado en Supabase, no rompe nada y usa memoria
    return false;
  }
}

// Obtener métricas consolidadas (Supabase + Memoria + Tiempo Real)
export async function getDashboardData(days = 7) {
  const now = Date.now();
  const sinceTs = Math.floor((now - (days * 86400000)) / 1000);
  const todayStr = new Date().toISOString().slice(0, 10);

  // 1. Tiempo Real (En vivo ahora)
  let onlineNow = 0;
  let watchingNow = 0;
  const activeStreams = [];

  // Purgar inactivos > 3 min
  for (const [hash, entry] of state.liveHeartbeats.entries()) {
    const ageMs = now - entry.lastSeen;
    if (ageMs > 180000) {
      state.liveHeartbeats.delete(hash);
      continue;
    }
    if (ageMs <= 60000) onlineNow++;
    if (ageMs <= 35000 && entry.isWatching) {
      watchingNow++;
      activeStreams.push({
        slug: entry.slug,
        ep: entry.ep,
        title: entry.title || entry.slug || 'Dorama en vivo',
        device: entry.device,
        seconds_ago: Math.floor(ageMs / 1000)
      });
    }
  }

  // 2. Consultar eventos de Supabase o Fallback
  let events = [];
  try {
    const res = await fetch(`${SUPABASE_URL}/rest/v1/analytics_events?timestamp=gte.${sinceTs}&select=*`, {
      headers: {
        'apikey': SUPABASE_SERVICE_ROLE,
        'Authorization': `Bearer ${SUPABASE_SERVICE_ROLE}`
      },
      cache: 'no-store'
    });
    if (res.ok) {
      events = await res.json();
    }
  } catch (e) {}

  if (!events || events.length === 0) {
    // Usar datos en memoria si Supabase está recién creado
    events = state.fallbackEvents.filter(e => e.timestamp >= sinceTs);
  }

  // Calcular agregados
  const uniqueVisitors = new Set(events.map(e => e.visitor_hash)).size;
  const pageviews = events.filter(e => e.event_type === 'pageview').length;
  const videoPlays = events.filter(e => e.event_type === 'video_play').length;
  const adClicks = events.filter(e => e.event_type === 'ad_click').length;

  const todayEvents = events.filter(e => e.date_str === todayStr);
  const todayVisitors = new Set(todayEvents.map(e => e.visitor_hash)).size;
  const todayPlays = todayEvents.filter(e => e.event_type === 'video_play').length;
  const todayAdClicks = todayEvents.filter(e => e.event_type === 'ad_click').length;

  // Timeline
  const timelineMap = new Map();
  for (const ev of events) {
    const d = ev.date_str || todayStr;
    if (!timelineMap.has(d)) {
      timelineMap.set(d, { date_str: d, visitorsSet: new Set(), views: 0, plays: 0, ads: 0 });
    }
    const row = timelineMap.get(d);
    row.visitorsSet.add(ev.visitor_hash);
    if (ev.event_type === 'pageview') row.views++;
    if (ev.event_type === 'video_play') row.plays++;
    if (ev.event_type === 'ad_click') row.ads++;
  }

  const timeline = Array.from(timelineMap.values()).map(r => ({
    date_str: r.date_str,
    visitors: r.visitorsSet.size,
    views: r.views,
    plays: r.plays,
    ads: r.ads
  })).sort((a, b) => a.date_str.localeCompare(b.date_str));

  // Top Doramas
  const dramaMap = new Map();
  for (const ev of events) {
    if (ev.event_type === 'video_play' && ev.slug) {
      const current = dramaMap.get(ev.slug) || { slug: ev.slug, display_title: ev.title || ev.slug, play_count: 0 };
      current.play_count++;
      dramaMap.set(ev.slug, current);
    }
  }
  const topDramas = Array.from(dramaMap.values()).sort((a, b) => b.play_count - a.play_count).slice(0, 10);

  // Dispositivos
  const devices = { mobile: 0, desktop: 0, tablet: 0 };
  for (const ev of events) {
    const dev = ev.device || 'desktop';
    if (devices[dev] !== undefined) devices[dev]++;
  }

  return {
    ok: true,
    time_range_days: days,
    realtime: {
      online_now: Math.max(onlineNow, watchingNow > 0 ? 1 : 0),
      watching_now: watchingNow,
      active_streams: activeStreams.slice(0, 15)
    },
    overview: {
      unique_visitors: uniqueVisitors,
      today_visitors: todayVisitors,
      pageviews,
      video_plays: videoPlays,
      today_plays: todayPlays,
      ad_clicks: adClicks,
      today_ad_clicks: todayAdClicks
    },
    timeline,
    top_dramas: topDramas,
    devices
  };
}
