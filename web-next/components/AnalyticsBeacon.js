'use client';
import { useEffect } from 'react';
import { usePathname, useSearchParams } from 'next/navigation';
import { trackPageView } from '../lib/analytics';

export default function AnalyticsBeacon() {
  const pathname = usePathname();
  const searchParams = useSearchParams();

  useEffect(() => {
    // Don't track admin panel pageviews in public visitor count
    if (pathname && !pathname.startsWith('/admin')) {
      const fullPath = pathname + (searchParams?.toString() ? '?' + searchParams.toString() : '');
      trackPageView(fullPath);
    }
  }, [pathname, searchParams]);

  return null;
}
