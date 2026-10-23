'use client';
import { useEffect } from 'react';
import { usePathname } from 'next/navigation';
import { AD_SOCIALBAR_SRC } from '../lib/adsterraAds';

/**
 * Inyecta el Social Bar dinámico de Adsterra de forma no invasiva.
 * No se ejecuta en las pantallas de administración ni interrumpe la navegación.
 */
export default function AdsterraSocialBar() {
  const pathname = usePathname();

  useEffect(() => {
    // No cargar en el panel de administración
    if (pathname && pathname.startsWith('/admin')) return;

    // Evitar duplicaciones del script
    if (document.getElementById('adsterra-socialbar-script')) return;

    try {
      const script = document.createElement('script');
      script.id = 'adsterra-socialbar-script';
      script.setAttribute('data-cfasync', 'false');
      script.src = AD_SOCIALBAR_SRC;
      script.async = true;
      document.body.appendChild(script);
    } catch (e) {
      // Fail silently
    }
  }, [pathname]);

  return null;
}
