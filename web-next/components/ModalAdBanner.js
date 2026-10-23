'use client';
import { useState, useEffect } from 'react';
import AdsterraBanner from './AdsterraBanner';
import { BANNER_300x250_KEY, BANNER_320x50_KEY } from '../lib/adsterraAds';

/**
 * Banner adaptable dentro del Modal de Títulos:
 * - Escritorio (>= 768px): Muestra el banner 300x250 en la columna izquierda bajo la sinopsis
 * - Móviles y Tablets (< 768px): Muestra el banner delgado 320x50 (solo 50px de alto) para no empujar los episodios
 * - Auto-colapso: Si un adblocker bloquea el anuncio, se oculta para no dejar huecos vacíos.
 */
export default function ModalAdBanner({ className = '' }) {
  const [isSmallScreen, setIsSmallScreen] = useState(false);
  const [mounted, setMounted] = useState(false);
  const [isBlocked, setIsBlocked] = useState(false);

  useEffect(() => {
    setMounted(true);
    const checkSize = () => setIsSmallScreen(window.innerWidth < 768);
    checkSize();
    window.addEventListener('resize', checkSize);
    return () => window.removeEventListener('resize', checkSize);
  }, []);

  if (isBlocked) return null;

  return (
    <div className={`modal-ad-banner-slot ${isSmallScreen ? 'modal-ad-banner-mobile' : ''} ${className}`}>
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
            zoneKey={BANNER_300x250_KEY} 
            width={300} 
            height={250} 
            onBlocked={() => setIsBlocked(true)} 
          />
        )
      )}
    </div>
  );
}
