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
    fallbackEvents: [],        // eventos locales en memoria de respaldo
    fallbackErrorLogs: []      // logs de errores en memoria de respaldo
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

export function detectOS(ua = '') {
  const low = (ua || '').toLowerCase();
  if (low.includes('iphone') || low.includes('ipad') || low.includes('ios')) return 'iOS';
  if (low.includes('android')) return 'Android';
  if (low.includes('windows')) return 'Windows';
  if (low.includes('macintosh') || low.includes('mac os')) return 'macOS';
  if (low.includes('linux')) return 'Linux';
  return 'Otro';
}

export function detectBrowser(ua = '') {
  const low = (ua || '').toLowerCase();
  if (low.includes('edg/')) return 'Edge';
  if (low.includes('samsungbrowser')) return 'Samsung Internet';
  if (low.includes('chrome') && !low.includes('edg/')) return 'Chrome';
  if (low.includes('safari') && !low.includes('chrome')) return 'Safari';
  if (low.includes('firefox')) return 'Firefox';
  if (low.includes('opera') || low.includes('opr/')) return 'Opera';
  return 'Navegador Móvil';
}

export function getCountryDetails(code = 'PE') {
  const c = (code || 'PE').toUpperCase().trim();
  const map = {
    'PE': { name: 'Perú', flag: '🇵🇪' },
    'MX': { name: 'México', flag: '🇲🇽' },
    'US': { name: 'Estados Unidos', flag: '🇺🇸' },
    'CO': { name: 'Colombia', flag: '🇨🇴' },
    'AR': { name: 'Argentina', flag: '🇦🇷' },
    'CL': { name: 'Chile', flag: '🇨🇱' },
    'ES': { name: 'España', flag: '🇪🇸' },
    'EC': { name: 'Ecuador', flag: '🇪🇨' },
    'BO': { name: 'Bolivia', flag: '🇧🇴' },
    'GT': { name: 'Guatemala', flag: '🇬🇹' },
    'DO': { name: 'Rep. Dominicana', flag: '🇩🇴' },
    'VE': { name: 'Venezuela', flag: '🇻🇪' },
    'CR': { name: 'Costa Rica', flag: '🇨🇷' },
    'PA': { name: 'Panamá', flag: '🇵🇦' },
    'UY': { name: 'Uruguay', flag: '🇺🇾' },
    'PY': { name: 'Paraguay', flag: '🇵🇾' },
    'HN': { name: 'Honduras', flag: '🇭🇳' },
    'SV': { name: 'El Salvador', flag: '🇸🇻' },
    'NI': { name: 'Nicaragua', flag: '🇳🇮' },
    'BR': { name: 'Brasil', flag: '🇧🇷' }
  };
  return map[c] || { name: c || 'Desconocido', flag: '🌍' };
}

export function recordLiveHeartbeat(isWatching, slug = '', ep = '', title = '', ip = '127.0.0.1', ua = '', country = 'PE', city = '') {
  const visitorHash = hashVisitor(ip, ua);
  const device = detectDevice(ua);
  const countryInfo = getCountryDetails(country);
  state.liveHeartbeats.set(visitorHash, {
    lastSeen: Date.now(),
    isWatching: Boolean(isWatching),
    slug: slug || '',
    ep: String(ep || ''),
    title: title || '',
    device,
    country: country.toUpperCase(),
    country_name: countryInfo.name,
    flag: countryInfo.flag,
    city: city || ''
  });
}

// Guardar evento en Supabase Cloud con respaldo en memoria y compatibilidad garantizada
export async function saveEvent(eventData) {
  const now = Date.now();
  const dateStr = new Date(now).toISOString().slice(0, 10);
  const hourStr = new Date(now).toISOString().slice(0, 13) + ':00';

  const countryCode = (eventData.country || 'PE').toUpperCase().trim();
  const countryInfo = getCountryDetails(countryCode);

  const baseDoc = {
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
    country: countryCode
  };

  const extendedDoc = {
    ...baseDoc,
    city: eventData.city || '',
    region: eventData.region || '',
    country_name: countryInfo.name,
    network: eventData.network || (eventData.event_type === 'ad_click' ? eventData.title : ''),
    ad_step: eventData.ad_step || 1,
    os: eventData.os || '',
    browser: eventData.browser || ''
  };

  // Mantener copia en memoria
  state.fallbackEvents.push(extendedDoc);
  if (state.fallbackEvents.length > 5000) state.fallbackEvents.shift();

  // Actualizar telemetría viva
  state.liveHeartbeats.set(baseDoc.visitor_hash, {
    lastSeen: now,
    isWatching: baseDoc.event_type === 'video_play',
    slug: baseDoc.slug,
    ep: baseDoc.ep,
    title: baseDoc.title,
    device: baseDoc.device,
    country: countryCode,
    country_name: countryInfo.name,
    flag: countryInfo.flag,
    city: eventData.city || ''
  });

  // Guardar en Supabase REST con fallback automático
  try {
    let res = await fetch(`${SUPABASE_URL}/rest/v1/analytics_events`, {
      method: 'POST',
      headers: {
        'apikey': SUPABASE_SERVICE_ROLE,
        'Authorization': `Bearer ${SUPABASE_SERVICE_ROLE}`,
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
      },
      body: JSON.stringify(extendedDoc),
      cache: 'no-store'
    });
    if (!res.ok && res.status === 400) {
      // Si el usuario aún no ejecutó el SQL para las nuevas columnas, guardar con esquema base
      res = await fetch(`${SUPABASE_URL}/rest/v1/analytics_events`, {
        method: 'POST',
        headers: {
          'apikey': SUPABASE_SERVICE_ROLE,
          'Authorization': `Bearer ${SUPABASE_SERVICE_ROLE}`,
          'Content-Type': 'application/json',
          'Prefer': 'return=minimal'
        },
        body: JSON.stringify(baseDoc),
        cache: 'no-store'
      });
    }
    return res.ok;
  } catch (err) {
    return false;
  }
}

// Helper para obtener conteo exacto de Supabase mediante encabezados Range (sin límite de 1000)
async function getExactCount(filterQuery) {
  try {
    const res = await fetch(`${SUPABASE_URL}/rest/v1/analytics_events?${filterQuery}&select=id`, {
      headers: {
        'apikey': SUPABASE_SERVICE_ROLE,
        'Authorization': `Bearer ${SUPABASE_SERVICE_ROLE}`,
        'Prefer': 'count=exact',
        'Range-Unit': 'items',
        'Range': '0-0'
      },
      cache: 'no-store'
    });
    const cr = res.headers.get('content-range') || '';
    if (cr.includes('/')) {
      return parseInt(cr.split('/')[1], 10) || 0;
    }
  } catch (e) {}
  return 0;
}

// Obtener métricas consolidadas exactas (Supabase + Memoria + Tiempo Real)
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
        country: entry.country || 'PE',
        country_name: entry.country_name || 'Perú',
        flag: entry.flag || '🇵🇪',
        city: entry.city || '',
        seconds_ago: Math.floor(ageMs / 1000)
      });
    }
  }

  // 2. Conteo EXACTO en paralelo desde Supabase (Previene bug de truncado a 1000 filas de PostgREST)
  const countHeaders = {
    'apikey': SUPABASE_SERVICE_ROLE,
    'Authorization': `Bearer ${SUPABASE_SERVICE_ROLE}`
  };

  const [
    adClicksTodayCount,
    adClicksRangeCount,
    pageviewsTodayCount,
    pageviewsRangeCount,
    playsTodayCount,
    playsRangeCount,
    recentEventsRes
  ] = await Promise.all([
    getExactCount(`date_str=eq.${todayStr}&event_type=eq.ad_click`),
    getExactCount(`timestamp=gte.${sinceTs}&event_type=eq.ad_click`),
    getExactCount(`date_str=eq.${todayStr}&event_type=eq.pageview`),
    getExactCount(`timestamp=gte.${sinceTs}&event_type=eq.pageview`),
    getExactCount(`date_str=eq.${todayStr}&event_type=eq.video_play`),
    getExactCount(`timestamp=gte.${sinceTs}&event_type=eq.video_play`),
    fetch(`${SUPABASE_URL}/rest/v1/analytics_events?timestamp=gte.${sinceTs}&order=timestamp.desc&limit=1000`, {
      headers: countHeaders,
      cache: 'no-store'
    }).catch(() => null)
  ]);

  let recentEvents = [];
  if (recentEventsRes && recentEventsRes.ok) {
    try {
      recentEvents = await recentEventsRes.json();
    } catch (_) {}
  }

  if (!recentEvents || recentEvents.length === 0) {
    recentEvents = state.fallbackEvents.filter(e => e.timestamp >= sinceTs);
  }

  // Métricas de Visitantes Únicos
  const uniqueVisitors = new Set(recentEvents.map(e => e.visitor_hash)).size;
  const todayEvents = recentEvents.filter(e => e.date_str === todayStr);
  const todayVisitors = new Set(todayEvents.map(e => e.visitor_hash)).size;

  // Timeline diario (Visitas, Plays, Anuncios)
  const timelineMap = new Map();
  for (const ev of recentEvents) {
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

  // Top Doramas Más Vistos
  const dramaMap = new Map();
  for (const ev of recentEvents) {
    if (ev.event_type === 'video_play' && ev.slug) {
      const current = dramaMap.get(ev.slug) || { slug: ev.slug, display_title: ev.title || ev.slug, play_count: 0 };
      current.play_count++;
      dramaMap.set(ev.slug, current);
    }
  }
  const topDramas = Array.from(dramaMap.values()).sort((a, b) => b.play_count - a.play_count).slice(0, 10);

  // Desglose de Dispositivos
  const devices = { mobile: 0, desktop: 0, tablet: 0 };
  const osBreakdown = {};
  for (const ev of recentEvents) {
    const dev = ev.device || 'desktop';
    if (devices[dev] !== undefined) devices[dev]++;
    const os = ev.os || (dev === 'mobile' ? 'Móvil' : 'Desktop');
    osBreakdown[os] = (osBreakdown[os] || 0) + 1;
  }

  // Desglose Geográfico por Países
  const countryMap = new Map();
  const cityMap = new Map();
  for (const ev of recentEvents) {
    const code = (ev.country || 'PE').toUpperCase();
    const cInfo = getCountryDetails(code);
    const cEntry = countryMap.get(code) || { code, name: cInfo.name, flag: cInfo.flag, count: 0 };
    cEntry.count++;
    countryMap.set(code, cEntry);

    if (ev.city && ev.city.trim()) {
      const cityKey = `${ev.city.trim()}, ${code}`;
      cityMap.set(cityKey, (cityMap.get(cityKey) || 0) + 1);
    }
  }

  const totalGeoEvents = Math.max(recentEvents.length, 1);
  const countries = Array.from(countryMap.values())
    .map(c => ({
      ...c,
      pct: Math.round((c.count / totalGeoEvents) * 100)
    }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 10);

  const topCities = Array.from(cityMap.entries())
    .map(([city, count]) => ({ city, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 8);

  // Desglose de Redes de Anuncios y Clics Recientes
  const adNetworks = { monetag: 0, adsterra: 0, total: 0 };
  const recentAdClicks = [];
  for (const ev of recentEvents) {
    if (ev.event_type === 'ad_click') {
      const net = (ev.network || ev.title || 'monetag').toLowerCase();
      if (net.includes('monetag')) adNetworks.monetag++;
      else if (net.includes('adsterra')) adNetworks.adsterra++;
      else adNetworks.monetag++;
      adNetworks.total++;

      if (recentAdClicks.length < 12) {
        const cInfo = getCountryDetails(ev.country);
        recentAdClicks.push({
          slug: ev.slug,
          ep: ev.ep || '1',
          title: ev.title || ev.slug || 'Dorama',
          network: net.includes('adsterra') ? 'Adsterra' : 'Monetag',
          device: ev.device || 'mobile',
          country: cInfo.name,
          flag: cInfo.flag,
          city: ev.city || '',
          timestamp: ev.timestamp,
          time_str: new Date(ev.timestamp * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        });
      }
    }
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
      pageviews: Math.max(pageviewsRangeCount, recentEvents.filter(e => e.event_type === 'pageview').length),
      today_pageviews: Math.max(pageviewsTodayCount, todayEvents.filter(e => e.event_type === 'pageview').length),
      video_plays: Math.max(playsRangeCount, recentEvents.filter(e => e.event_type === 'video_play').length),
      today_plays: Math.max(playsTodayCount, todayEvents.filter(e => e.event_type === 'video_play').length),
      ad_clicks: Math.max(adClicksRangeCount, recentEvents.filter(e => e.event_type === 'ad_click').length),
      today_ad_clicks: Math.max(adClicksTodayCount, todayEvents.filter(e => e.event_type === 'ad_click').length)
    },
    timeline,
    top_dramas: topDramas,
    devices,
    os_breakdown: osBreakdown,
    countries,
    cities: topCities,
    ad_networks: adNetworks,
    recent_ad_clicks: recentAdClicks
  };
}

// ==========================================================
// 🛡️ GESTIÓN INTELIGENTE DE ERRORES DE VIDEO (SUPABASE)
// ==========================================================

// Guardar registro de error de video en Supabase Cloud con autolimpieza de 7 días
export async function saveVideoErrorLog(data = {}) {
  const doc = {
    slug: data.slug || '',
    ep: String(data.ep || ''),
    title: data.title || '',
    error_type: data.error_type || 'UNKNOWN',
    http_status: data.http_status ? parseInt(data.http_status, 10) : null,
    stream_url: data.stream_url || '',
    error_message: data.error_message || '',
    details: data.details || {},
    device: data.device || 'desktop',
    user_agent: data.user_agent || '',
    status: 'pending'
  };

  // Mantener copia en memoria para disponibilidad inmediata
  if (!state.fallbackErrorLogs) state.fallbackErrorLogs = [];
  state.fallbackErrorLogs.unshift({
    id: 'mem_' + Date.now() + '_' + Math.floor(Math.random() * 1000),
    created_at: new Date().toISOString(),
    ...doc
  });
  if (state.fallbackErrorLogs.length > 500) state.fallbackErrorLogs.pop();

  // Limpieza automática de registros mayores a 7 días en Supabase
  try {
    const sevenDaysAgo = new Date(Date.now() - (7 * 86400000)).toISOString();
    fetch(`${SUPABASE_URL}/rest/v1/video_error_logs?created_at=lt.${encodeURIComponent(sevenDaysAgo)}`, {
      method: 'DELETE',
      headers: {
        'apikey': SUPABASE_SERVICE_ROLE,
        'Authorization': `Bearer ${SUPABASE_SERVICE_ROLE}`
      }
    }).catch(() => {});
  } catch (e) {}

  // Guardar en Supabase REST
  try {
    const res = await fetch(`${SUPABASE_URL}/rest/v1/video_error_logs`, {
      method: 'POST',
      headers: {
        'apikey': SUPABASE_SERVICE_ROLE,
        'Authorization': `Bearer ${SUPABASE_SERVICE_ROLE}`,
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
      },
      body: JSON.stringify(doc),
      cache: 'no-store'
    });
    if (res.ok) {
      const inserted = await res.json();
      return { ok: true, data: inserted };
    }
  } catch (err) {}

  return { ok: true, fallback: true };
}

// Obtener la lista de errores para el panel de administración
export async function getVideoErrorLogs() {
  try {
    const res = await fetch(`${SUPABASE_URL}/rest/v1/video_error_logs?status=eq.pending&order=created_at.desc&limit=100`, {
      headers: {
        'apikey': SUPABASE_SERVICE_ROLE,
        'Authorization': `Bearer ${SUPABASE_SERVICE_ROLE}`
      },
      cache: 'no-store'
    });
    if (res.ok) {
      const data = await res.json();
      return { ok: true, logs: data };
    }
  } catch (err) {}

  // Fallback a memoria si Supabase está offline
  const memLogs = (state.fallbackErrorLogs || []).filter(l => l.status !== 'resolved');
  return { ok: true, logs: memLogs, fallback: true };
}

// Marcar como resuelto / eliminar error de Supabase
export async function resolveVideoErrorLog(id) {
  if (!id) return { ok: false, error: 'ID requerido' };

  // Remover de memoria
  if (state.fallbackErrorLogs) {
    state.fallbackErrorLogs = state.fallbackErrorLogs.filter(l => String(l.id) !== String(id));
  }

  // Eliminar de Supabase
  try {
    const res = await fetch(`${SUPABASE_URL}/rest/v1/video_error_logs?id=eq.${id}`, {
      method: 'DELETE',
      headers: {
        'apikey': SUPABASE_SERVICE_ROLE,
        'Authorization': `Bearer ${SUPABASE_SERVICE_ROLE}`
      }
    });
    return { ok: res.ok };
  } catch (err) {
    return { ok: false, error: err.message };
  }
}
