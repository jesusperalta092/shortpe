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
