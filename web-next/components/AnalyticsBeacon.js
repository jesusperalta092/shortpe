'use client';
import { useEffect } from 'react';
import { usePathname, useSearchParams } from 'next/navigation';
import { trackPageView, trackLiveHeartbeat } from '../lib/analytics';

export default function AnalyticsBeacon() {
  const pathname = usePathname();
  const searchParams = useSearchParams();

  useEffect(() => {
    // Don't track admin panel pageviews in public visitor count
    if (pathname && !pathname.startsWith('/admin')) {
      const fullPath = pathname + (searchParams?.toString() ? '?' + searchParams.toString() : '');
      trackPageView(fullPath);
      trackLiveHeartbeat(false);

      // Enviar pulso de presencia cada 25s
      const timer = setInterval(() => {
        trackLiveHeartbeat(false);
      }, 25000);

      return () => clearInterval(timer);
    }
  }, [pathname, searchParams]);

  return null;
}
