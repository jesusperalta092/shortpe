'use client';
import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { getHistory, removeFromHistory } from '../lib/watchHistory';

export default function ContinueWatching({ onOpenModal }) {
  const [items, setItems] = useState([]);
  const [mounted, setMounted] = useState(false);
  const trackRef = useRef(null);

  const loadItems = () => {
    const list = getHistory();
    setItems(list);
  };

  useEffect(() => {
    setMounted(true);
    loadItems();

    const handleHistoryChange = () => loadItems();
    window.addEventListener('dramape_history_change', handleHistoryChange);
    window.addEventListener('storage', handleHistoryChange);

    return () => {
      window.removeEventListener('dramape_history_change', handleHistoryChange);
      window.removeEventListener('storage', handleHistoryChange);
    };
  }, []);

  if (!mounted || !items || items.length === 0) {
    return null;
  }

  const scroll = (dir) => {
    const t = trackRef.current;
    if (t) t.scrollBy({ left: dir * (t.clientWidth * 0.8), behavior: 'smooth' });
  };

  const handleDismiss = (e, slug) => {
    e.stopPropagation();
    e.preventDefault();
    removeFromHistory(slug);
  };

  const getCardImg = (item) => {
    const raw = item.poster;
    if (!raw) return '/favicon.ico';
    if (raw.startsWith('http://localhost') || raw.startsWith('http://127.0.0.1')) return '/favicon.ico';
    if (raw.startsWith('/') || raw.startsWith('data:')) return raw;
    return '/proxy/img?url=' + encodeURIComponent(raw);
  };

  return (
    <section className="row continue-watching-section">
      <div className="row-header-wrap">
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <h2 className="row-title">
            <span className="bar" style={{ background: '#ef4444' }} />
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
              <span>▶️</span> Continuar Viendo
            </span>
          </h2>
          <span className="continue-count-badge">
            {items.length} {items.length === 1 ? 'dorama' : 'doramas'}
          </span>
        </div>
      </div>

      <div className="carousel continue-carousel">
        <button className="nav-arrow left" onClick={() => scroll(-1)} aria-label="Anterior">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="m15 18-6-6 6-6" /></svg>
        </button>
        <button className="nav-arrow right" onClick={() => scroll(1)} aria-label="Siguiente">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="m9 18 6-6-6-6" /></svg>
        </button>

        <div className="carousel-track continue-track" ref={trackRef}>
          {items.map((item) => {
            const total = parseInt(item.total_eps, 10) || 0;
            const seenCount = item.vistos ? item.vistos.length : 1;
            const progressPct = total > 0 ? Math.min(100, Math.round((seenCount / total) * 100)) : 10;

            return (
              <div key={item.slug} className="continue-card">
                {/* Botón descartar de la lista */}
                <button
                  className="continue-dismiss-btn"
                  onClick={(e) => handleDismiss(e, item.slug)}
                  title="Quitar de continuar viendo"
                  aria-label="Quitar de continuar viendo"
                >
                  ✕
                </button>

                <Link
                  href={`/ver/${item.slug}/${item.last_ep || '1'}`}
                  className="continue-card-poster-wrap"
                  scroll={false}
                  onClick={() => {
                    if (typeof window !== 'undefined') {
                      sessionStorage.setItem('dramia_last_section', '/');
                    }
                  }}
                >
                  <img
                    src={getCardImg(item)}
                    alt={item.title}
                    loading="lazy"
                    onError={(e) => {
                      e.currentTarget.style.display = 'none';
                    }}
                  />

                  {/* Badge de último episodio */}
                  <div className="continue-ep-badge">
                    Cap. {item.last_ep}
                  </div>

                  {/* Overlay con icono de Play animado */}
                  <div className="continue-play-overlay">
                    <div className="continue-play-circle">
                      <svg viewBox="0 0 24 24" fill="white" width="22" height="22">
                        <path d="M8 5v14l11-7z" />
                      </svg>
                    </div>
                    <span className="continue-play-text">Continuar</span>
                  </div>

                  {/* Barra de progreso estilo Netflix al pie del póster */}
                  <div className="continue-progress-bar-bg">
                    <div
                      className="continue-progress-bar-fill"
                      style={{ width: `${Math.max(12, progressPct)}%` }}
                    />
                  </div>
                </Link>

                <div className="continue-card-info" onClick={() => onOpenModal && onOpenModal(item.slug)}>
                  <h3 className="continue-card-title" title={item.title}>
                    {item.title}
                  </h3>
                  <div className="continue-card-meta">
                    <span className="continue-card-sub">
                      Episodio {item.last_ep} {total > 0 ? `de ${total}` : ''}
                    </span>
                    <span className="continue-card-dot">•</span>
                    <span className="continue-card-pct">
                      {progressPct}% visto
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
