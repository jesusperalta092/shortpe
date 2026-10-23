'use client';
import { useState, useEffect } from 'react';
import AdsterraBanner from './AdsterraBanner';
import { BANNER_728x90_KEY, BANNER_300x250_KEY } from '../lib/adsterraAds';

/**
 * Banner de encabezado adaptable para Secciones:
 * - Escritorio (>= 768px): Muestra el banner Leaderboard 728x90 (Espacio superior pedido por el usuario)
 * - Móvil (< 768px): Muestra el banner Rectángulo 300x250 para adaptarse perfectamente a la pantalla
 */
export default function SectionAdBanner({ className = '' }) {
  const [isMobile, setIsMobile] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const checkSize = () => setIsMobile(window.innerWidth < 768);
    checkSize();
    window.addEventListener('resize', checkSize);
    return () => window.removeEventListener('resize', checkSize);
  }, []);

  return (
    <div className={`section-ad-banner-wrap ${className}`}>
      <div className="ad-badge-label">PUBLICIDAD</div>
      {mounted && (
        isMobile ? (
          <AdsterraBanner zoneKey={BANNER_300x250_KEY} width={300} height={250} />
        ) : (
          <AdsterraBanner zoneKey={BANNER_728x90_KEY} width={728} height={90} />
        )
      )}
    </div>
  );
}
