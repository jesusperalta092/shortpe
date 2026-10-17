// Client-side analytics & telemetry library for DramaPe
export function trackEvent(eventType, payload = {}) {
  if (typeof window === 'undefined') return;
  try {
    const data = {
      event_type: eventType,
      path: payload.path || window.location.pathname,
      slug: payload.slug || '',
      ep: String(payload.ep || ''),
      title: payload.title || '',
      timestamp: Date.now()
    };

    if (navigator.sendBeacon) {
      const blob = new Blob([JSON.stringify(data)], { type: 'application/json' });
      navigator.sendBeacon('/api/analytics/track', blob);
    } else {
      fetch('/api/analytics/track', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
        keepalive: true
      }).catch(() => {});
    }
  } catch (e) {
    // Fail silently
  }
}

export function trackPageView(path) {
  trackEvent('pageview', { path: path || window.location.pathname });
}

export function trackVideoPlay(slug, ep, title) {
  trackEvent('video_play', { slug, ep, title });
}

export function trackAdClick(slug, ep, network = 'ad') {
  trackEvent('ad_click', { slug, ep, title: network });
}

export function trackLiveHeartbeat(isWatching = false, slug = '', ep = '', title = '') {
  if (typeof window === 'undefined') return;
  try {
    const data = {
      is_watching: isWatching,
      slug: slug || '',
      ep: String(ep || ''),
      title: title || ''
    };
    if (navigator.sendBeacon) {
      const blob = new Blob([JSON.stringify(data)], { type: 'application/json' });
      navigator.sendBeacon('/api/analytics/heartbeat', blob);
    } else {
      fetch('/api/analytics/heartbeat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
        keepalive: true
      }).catch(() => {});
    }
  } catch (e) {}
}

export async function authenticateAdmin(pin) {
  try {
    const res = await fetch('/api/analytics/auth', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pin: (pin || '').trim() })
    });
    const data = await res.json();
    return data;
  } catch (e) {
    return { ok: false, error: 'Error de conexión con el servidor' };
  }
}

export async function fetchAdminDashboard(days = 7, token = '') {
  try {
    const headers = {};
    if (token) headers['Authorization'] = 'Bearer ' + token;
    const res = await fetch('/api/analytics/dashboard?days=' + days, {
      headers,
      cache: 'no-store'
    });
    if (res.status === 401) {
      return { ok: false, unauthorized: true, error: 'Sesión expirada o no autorizada' };
    }
    const data = await res.json();
    return data;
  } catch (e) {
    return { ok: false, error: 'Error al cargar analíticas' };
  }
}

// Envío automático e inteligente de errores de video sin requerir acción del usuario
export function reportVideoError(errorData = {}) {
  if (typeof window === 'undefined') return;
  try {
    const payload = {
      slug: errorData.slug || '',
      ep: String(errorData.ep || ''),
      title: errorData.title || '',
      error_type: errorData.error_type || 'UNKNOWN_VIDEO_ERROR',
      http_status: errorData.http_status || null,
      stream_url: errorData.stream_url || '',
      error_message: errorData.error_message || '',
      details: errorData.details || {},
      device: /Mobi|Android|iPhone/i.test(navigator.userAgent) ? 'mobile' : /iPad|Tablet/i.test(navigator.userAgent) ? 'tablet' : 'desktop',
      user_agent: navigator.userAgent || ''
    };

    if (navigator.sendBeacon) {
      const blob = new Blob([JSON.stringify(payload)], { type: 'application/json' });
      navigator.sendBeacon('/api/analytics/error-report', blob);
    } else {
      fetch('/api/analytics/error-report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        keepalive: true
      }).catch(() => {});
    }
  } catch (e) {
    // Fail silently
  }
}

// Consultar lista de errores para el panel administrativo
export async function fetchAdminErrorLogs(token = '') {
  try {
    const headers = {};
    if (token) headers['Authorization'] = 'Bearer ' + token;
    const res = await fetch('/api/analytics/admin-errors', {
      headers,
      cache: 'no-store'
    });
    if (res.status === 401) return { ok: false, unauthorized: true };
    return await res.json();
  } catch (e) {
    return { ok: false, error: 'Error al consultar logs de errores' };
  }
}

// Marcar como resuelto / eliminar error de Supabase
export async function resolveAdminErrorLog(id, token = '') {
  try {
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = 'Bearer ' + token;
    const res = await fetch('/api/analytics/admin-errors', {
      method: 'DELETE',
      headers,
      body: JSON.stringify({ id })
    });
    return await res.json();
  } catch (e) {
    return { ok: false, error: 'Error al resolver log' };
  }
}
