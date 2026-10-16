'use client';
import { useRef } from 'react';

export default function Carousel({ 
  title, 
  items, 
  onOpen, 
  onMore, 
  moreLabel, 
  variant = 'default',
  remainingCount = 0,
  totalCount = 0
}) {
  const trackRef = useRef(null);
  if (!items || !items.length) return null;
  const scroll = (dir) => {
    const t = trackRef.current;
    if (t) t.scrollBy({ left: dir * (t.clientWidth * 0.8), behavior: 'smooth' });
  };

  const isKurz = variant === 'kurzdrama';

  return (
    <section className={`row ${isKurz ? 'kurz-row' : ''}`}>
      {title && (
        <div className="row-header-wrap">
          <h2 className="row-title"><span className="bar" />{title}</h2>
          {onMore && (
            <button className="row-more-btn" onClick={onMore} aria-label={`Ver más de ${title}`}>
              <span>{moreLabel || 'Ver más +'}</span>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="m9 18 6-6-6-6"/></svg>
            </button>
          )}
        </div>
      )}
      <div className={`carousel ${isKurz ? 'kurz-carousel' : ''}`}>
        <button className="nav-arrow left" onClick={() => scroll(-1)} aria-label="Anterior">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="m15 18-6-6 6-6" /></svg>
        </button>
        <button className="nav-arrow right" onClick={() => scroll(1)} aria-label="Siguiente">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="m9 18 6-6-6-6" /></svg>
        </button>
        <div className={`carousel-track ${isKurz ? 'kurz-track' : ''}`} ref={trackRef}>
          {items.map((d, i) => {
            if (isKurz) {
              return (
                <div key={d.slug + '-' + i} className="kurz-card" onClick={() => onOpen && onOpen(d.slug)}>
                  <div className="kurz-card-poster-wrap">
                    <img 
                      src={d.poster_local ? '/' + d.poster_local : (d.poster?.startsWith('http') ? '/proxy/img?url=' + encodeURIComponent(d.poster) : (d.poster || '/favicon.ico'))} 
                      alt={d.title} 
                      loading="lazy" 
                      onError={(e) => {
                        e.currentTarget.style.display = 'none';
                        if (e.currentTarget.nextElementSibling && e.currentTarget.nextElementSibling.classList.contains('kurz-poster-fallback')) {
                          e.currentTarget.nextElementSibling.style.display = 'flex';
                        }
                      }}
                    />
                    <div className="kurz-poster-fallback" style={{ display: d.poster || d.poster_local ? 'none' : 'flex' }}>
                      <span>{d.title}</span>
                    </div>
                    <span className="kurz-badge-ai">Ai</span>
                    <div className="kurz-play-overlay">
                      <div className="kurz-play-circle">
                        <svg viewBox="0 0 24 24" fill="white" width="20" height="20">
                          <path d="M8 5v14l11-7z" />
                        </svg>
                      </div>
                    </div>
                  </div>
                  <div className="kurz-card-info">
                    <h3 className="kurz-card-title" title={d.title}>{d.title}</h3>
                    <div className="kurz-card-meta">
                      <span className="kurz-card-eps">{d.total_episodes ? `${d.total_episodes} eps` : 'HD'}</span>
                      <span className="kurz-card-dot">•</span>
                      <span className="kurz-card-lang">Español</span>
                    </div>
                  </div>
                </div>
              );
            }

            return (
              <div key={d.slug + '-' + i} className="card" onClick={() => onOpen && onOpen(d.slug)}>
                {i < 3 && <div className={`card-tag top-${i + 1}`}>TOP {i + 1}</div>}
                <img 
                  src={d.poster_local ? '/' + d.poster_local : (d.poster?.startsWith('http') ? '/proxy/img?url=' + encodeURIComponent(d.poster) : (d.poster || '/favicon.ico'))} 
                  alt={d.title} 
                  loading="lazy" 
                  onError={(e) => {
                    e.currentTarget.style.display = 'none';
                    if (e.currentTarget.nextElementSibling && e.currentTarget.nextElementSibling.classList.contains('card-poster-fallback')) {
                      e.currentTarget.nextElementSibling.style.display = 'flex';
                    }
                  }}
                />
                <div className="card-poster-fallback" style={{ display: d.poster || d.poster_local ? 'none' : 'flex' }}>
                  <span className="card-fallback-text">{d.title}</span>
                </div>
                <div className="card-play"><svg viewBox="0 0 24 24" fill="white"><path d="M8 5v14l11-7z" /></svg></div>
                <div className="card-overlay">
                  <div className="card-title">{d.title}</div>
                  <div className="card-overlay-meta">
                    <span className="match">98%</span>
                    <span className="pill">+16</span>
                    <span>{d.total_episodes || '?'} eps</span>
                  </div>
                </div>
              </div>
            );
          })}

          {onMore && isKurz && (
            <div 
              className="kurz-card kurz-more-card" 
              onClick={onMore} 
              role="button" 
              tabIndex={0} 
              aria-label={moreLabel || 'Más +'}
            >
              <div className="kurz-card-poster-wrap kurz-more-poster-wrap">
                <div className="kurz-more-circle">
                  <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.8" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="12" y1="5" x2="12" y2="19" />
                    <line x1="5" y1="12" x2="19" y2="12" />
                  </svg>
                </div>
                <span className="kurz-more-text">{moreLabel || 'Más +'}</span>
                {remainingCount > 0 ? (
                  <span className="kurz-more-count">+{remainingCount} más</span>
                ) : (
                  <span className="kurz-more-count">Ver todos</span>
                )}
              </div>
              <div className="kurz-card-info">
                <h3 className="kurz-card-title kurz-more-title">Explorar todos</h3>
                <div className="kurz-card-meta">
                  <span className="kurz-more-sub">{totalCount ? `${totalCount} títulos` : 'Ver sección'}</span>
                </div>
              </div>
            </div>
          )}

          {onMore && !isKurz && (
            <div 
              className="card card-more-card" 
              onClick={onMore} 
              role="button" 
              tabIndex={0} 
              aria-label={moreLabel || 'Más +'}
            >
              <div className="card-more-inner">
                <div className="card-more-icon-glow">
                  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.8" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="12" y1="5" x2="12" y2="19" />
                    <line x1="5" y1="12" x2="19" y2="12" />
                  </svg>
                </div>
                <span className="card-more-label">{moreLabel || 'Más +'}</span>
                <span className="card-more-hint">Explorar todos</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

