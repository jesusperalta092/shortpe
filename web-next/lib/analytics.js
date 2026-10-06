// Client-side analytics sender for DramaPe
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
    // Fail silently so user experience is never interrupted
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
