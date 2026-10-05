'use client';
import { useState, useEffect, useCallback, useMemo } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import Carousel from './Carousel';
import TitleModal from './TitleModal';
import Header from './Header';
import Footer from './Footer';

export default function HomeClient({ catalog, sections, hotdramaItems, dramavibeItems }) {
  const [modalSlug, setModalSlug] = useState(null);
  const searchParams = useSearchParams();

  // 10 dramas destacados de HotDrama (DramaVibe) para la portada dinamica
  const heroDramas = useMemo(() => {
    if (dramavibeItems && dramavibeItems.length >= 5) {
      return dramavibeItems.slice(0, 10);
    }
    return (sections.drama && sections.drama.length >= 10
      ? sections.drama.slice(0, 10)
      : catalog.slice(0, 10));
  }, [dramavibeItems, sections.drama, catalog]);

  const [heroIndex, setHeroIndex] = useState(0);
  const [isPaused, setIsPaused] = useState(false);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      sessionStorage.setItem('dramia_last_section', '/');
    }
  }, []);

  // Si llega con ?open=slug (al volver del player), abrir el modal
  useEffect(() => {
    const open = searchParams.get('open');
    if (open) setModalSlug(open);
  }, [searchParams]);

  // Rotacion suave cada 5.5s (SE PAUSA si el usuario interactua o si el modal esta abierto)
  useEffect(() => {
    if (isPaused || modalSlug || heroDramas.length <= 1) return;
    const timer = setInterval(() => {
      setHeroIndex(prev => (prev + 1) % heroDramas.length);
    }, 5500);
    return () => clearInterval(timer);
  }, [isPaused, modalSlug, heroDramas.length]);

  const handleOpenModal = useCallback((slug) => {
    setModalSlug(slug);
    if (typeof window !== 'undefined') {
      const url = new URL(window.location.href);
      url.searchParams.set('open', slug);
      window.history.replaceState({}, '', url.pathname + url.search);
      sessionStorage.setItem('dramia_last_section', url.pathname + url.search);
    }
  }, []);

  const handleCloseModal = useCallback(() => {
    setModalSlug(null);
    if (typeof window !== 'undefined') {
      const url = new URL(window.location.href);
      url.searchParams.delete('open');
      window.history.replaceState({}, '', url.pathname + (url.search ? url.search : ''));
      sessionStorage.setItem('dramia_last_section', url.pathname + (url.search ? url.search : ''));
    }
  }, []);

  const nextHero = useCallback(() => setHeroIndex(prev => (prev + 1) % heroDramas.length), [heroDramas.length]);
  const prevHero = useCallback(() => setHeroIndex(prev => (prev - 1 + heroDramas.length) % heroDramas.length), [heroDramas.length]);

  const currentHero = heroDramas[heroIndex] || heroDramas[0];

  const getHeroImg = (item) => {
    if (!item) return '';
    const raw = item.poster_local ? '/' + item.poster_local : (item.poster || '');
    if (!raw) return '';
    if (raw.startsWith('/') || raw.startsWith('http://localhost') || raw.startsWith('http://127.0.0.1')) {
      return raw;
    }
    return '/proxy/img?url=' + encodeURIComponent(raw);
  };

  return (
    <>
      <Header stats={catalog.length} />

      <main>
        {currentHero && (
          <section
            className="hero"
            onMouseEnter={() => setIsPaused(true)}
            onMouseLeave={() => setIsPaused(false)}
            onTouchStart={() => setIsPaused(true)}
            onTouchEnd={() => setIsPaused(false)}
          >
            {/* Carrusel de 10 fondos con atmosfera ambient HD y transicion suave crossfade */}
            <div className="hero-bg-container">
              {heroDramas.map((item, idx) => {
                const img = getHeroImg(item);
                const isActive = idx === heroIndex;
                return (
                  <div
                    key={item.slug}
                    className={`hero-bg-slide ${isActive ? 'active' : ''}`}
                    style={{
                      backgroundImage: img ? `url('${img}')` : 'none',
                    }}
                  />
                );
              })}
            </div>

            <div className="hero-overlay" />

            {/* Controles de navegacion de portada (Next / Prev) */}
            <button className="hero-arrow prev" onClick={prevHero} aria-label="Anterior portada">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="15 18 9 12 15 6" />
              </svg>
            </button>
            <button className="hero-arrow next" onClick={nextHero} aria-label="Siguiente portada">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="9 18 15 12 9 6" />
              </svg>
            </button>

            {/* Contenedor principal del Hero en Alta Definicion */}
            <div className="hero-main-layout">
              {/* Contenido animado del drama activo (Izquierda) */}
              <div className="hero-content" key={currentHero.slug}>
                <div className="hero-badge">
                  <span className="dot" /> 🔥 TENDENCIA #{heroIndex + 1} EN HOTDRAMA
                </div>
                <h1 className="hero-title">{currentHero.title}</h1>
                <div className="hero-meta">
                  <span className="match">99% de afinidad</span>
                  <span className="pill">+16</span>
                  <span>{currentHero.total_episodes || '50'} episodios</span>
                  <span className="pill badge-hd">ULTRA HD 4K</span>
                  <span>{(currentHero.genres || []).slice(0, 3).join(' · ') || 'HotDrama'}</span>
                </div>
                <p className="hero-desc">{currentHero.description || 'Una apasionante historia llena de giros inesperados, romance y emociones intensas en alta definición.'}</p>
                <div className="hero-btns">
                  <Link className="btn btn-play" href={'/ver/' + currentHero.slug + '/1'} scroll={false}>
                    <svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z" /></svg> Reproducir
                  </Link>
                  <button className="btn btn-info" onClick={() => handleOpenModal(currentHero.slug)}>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                      <circle cx="12" cy="12" r="10" />
                      <line x1="12" y1="16" x2="12" y2="12" />
                      <line x1="12" y1="8" x2="12.01" y2="8" />
                    </svg>
                    <span>Más información</span>
                  </button>
                </div>
              </div>

              {/* Showcase de Poster en Ultra Alta Definición (Derecha) */}
              <div className="hero-poster-showcase" onClick={() => handleOpenModal(currentHero.slug)}>
                <div className="hero-poster-glow" style={{ backgroundImage: `url('${getHeroImg(currentHero)}')` }} />
                <div className="hero-poster-card">
                  <img
                    src={getHeroImg(currentHero)}
                    alt={currentHero.title}
                    className="hero-poster-img"
                    loading="eager"
                  />
                  <div className="hero-poster-glass">
                    <span className="hero-poster-rank">#{heroIndex + 1}</span>
                    <span className="hero-poster-tag">TOP TENDENCIA</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Paginación de puntos de la portada */}
            <div className="hero-dots-container">
              {heroDramas.map((_, dIdx) => (
                <button
                  key={dIdx}
                  className={`hero-dot ${dIdx === heroIndex ? 'active' : ''}`}
                  onClick={() => setHeroIndex(dIdx)}
                  aria-label={`Ir al drama ${dIdx + 1}`}
                />
              ))}
            </div>
          </section>
        )}


        <div className="rows">
          <Carousel title="🔥 Tendencias ahora" items={sections.drama?.slice(0, 24) || []} onOpen={handleOpenModal} />
          {sections.dramatube?.length > 0 && <Carousel title="🎬 DramaTube · Nuevos Subtitulados" items={sections.dramatube.slice(0, 24)} onOpen={handleOpenModal} />}
          {hotdramaItems?.length > 0 && <Carousel title="🔥 HotDrama · Exclusivos" items={hotdramaItems.slice(0, 24)} onOpen={handleOpenModal} />}
          {sections.dramashorts?.length > 0 && <Carousel title="⚡ DramaShorts · Selección Rápida" items={sections.dramashorts.slice(0, 24)} onOpen={handleOpenModal} />}
          {dramavibeItems?.length > 0 && <Carousel title="🌟 DramaVibe · Lo Más Visto" items={dramavibeItems.slice(0, 24)} onOpen={handleOpenModal} />}
          <Carousel title="✨ Agregados recientemente" items={[...catalog].reverse().slice(0, 24)} onOpen={handleOpenModal} />
        </div>
      </main>

      <Footer catalogCount={catalog.length} />

      <TitleModal slug={modalSlug} onClose={handleCloseModal} />
    </>
  );
}
