'use client';
import { useState, useEffect } from 'react';
import AdsterraBanner from './AdsterraBanner';
import { BANNER_728x90_KEY, BANNER_320x50_KEY } from '../lib/adsterraAds';

/**
 * Banner de encabezado adaptable para Secciones:
 * - Escritorio (>= 800px): Muestra el banner Leaderboard 728x90
 * - Móviles y Tablets (< 800px): Muestra el banner rectangular delgado 320x50 (solo 50px de altura)
 * - Auto-colapso: Si un bloqueador (como Brave) bloquea el anuncio, el contenedor desaparece completamente sin dejar huecos negros ni letreros huérfanos.
 */
export default function SectionAdBanner({ className = '' }) {
  const [isSmallScreen, setIsSmallScreen] = useState(false);
  const [mounted, setMounted] = useState(false);
  const [isBlocked, setIsBlocked] = useState(false);

  useEffect(() => {
    setMounted(true);
    const checkSize = () => setIsSmallScreen(window.innerWidth < 800);
    checkSize();
    window.addEventListener('resize', checkSize);
    return () => window.removeEventListener('resize', checkSize);
  }, []);

  if (isBlocked) return null;

  return (
    <div className={`section-ad-banner-wrap ${className}`}>
      <div className="ad-badge-label">PUBLICIDAD</div>
      {mounted && (
        isSmallScreen ? (
          <AdsterraBanner 
            zoneKey={BANNER_320x50_KEY} 
            width={320} 
            height={50} 
            onBlocked={() => setIsBlocked(true)} 
          />
        ) : (
          <AdsterraBanner 
            zoneKey={BANNER_728x90_KEY} 
            width={728} 
            height={90} 
            onBlocked={() => setIsBlocked(true)} 
          />
        )
      )}
    </div>
  );
}
