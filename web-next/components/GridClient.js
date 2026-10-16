'use client';
import { useState, useCallback, useEffect, useRef, useMemo } from 'react';
import { useSearchParams } from 'next/navigation';
import TitleModal from './TitleModal';

const PAGE_CHUNK = 48;

export default function GridClient({ items, label }) {
  const [modalSlug, setModalSlug] = useState(null);
  const [visibleCount, setVisibleCount] = useState(PAGE_CHUNK);
  const [q, setQ] = useState('');
  const sentinelRef = useRef(null);
  const searchParams = useSearchParams();

  useEffect(() => {
    if (typeof window !== 'undefined') {
      sessionStorage.setItem('dramia_last_section', window.location.pathname + window.location.search);
    }
  }, []);

  // Filtrado reactivo por buscador
  const filteredItems = useMemo(() => {
    if (!q.trim()) return items || [];
    const query = q.toLowerCase().trim();
    return (items || []).filter(d => 
      (d.title && d.title.toLowerCase().includes(query)) ||
      (d.genres && d.genres.some(g => g.toLowerCase().includes(query)))
    );
  }, [items, q]);

  // Reset de paginación al buscar
  useEffect(() => {
    setVisibleCount(PAGE_CHUNK);
  }, [q]);

  // Scroll infinito ultra fluido para miles de dramas sin saturar memoria
  useEffect(() => {
    const el = sentinelRef.current;
    if (!el) return;
    const observer = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting) {
        setVisibleCount((prev) => Math.min(prev + PAGE_CHUNK, filteredItems.length));
      }
    }, { rootMargin: '600px' });
    observer.observe(el);
    return () => observer.disconnect();
  }, [filteredItems.length]);

  // Si llega con ?open=slug (ej. al volver del reproductor), abrir el modal automáticamente
  useEffect(() => {
    const open = searchParams.get('open');
    if (open) {
      setModalSlug(open);
    }
  }, [searchParams]);

  const handleOpen = useCallback((slug) => {
    setModalSlug(slug);
    if (typeof window !== 'undefined') {
      const url = new URL(window.location.href);
      url.searchParams.set('open', slug);
      window.history.replaceState({}, '', url.pathname + url.search);
      sessionStorage.setItem('dramia_last_section', url.pathname + url.search);
    }
  }, []);

  const handleClose = useCallback(() => {
    setModalSlug(null);
    if (typeof window !== 'undefined') {
      const url = new URL(window.location.href);
      url.searchParams.delete('open');
      window.history.replaceState({}, '', url.pathname + (url.search ? url.search : ''));
      sessionStorage.setItem('dramia_last_section', url.pathname + (url.search ? url.search : ''));
    }
  }, []);

  const visibleItems = filteredItems.slice(0, visibleCount);

  return (
    <>
      <div className="dv-search-wrap" style={{ marginBottom: 18 }}>
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder={`Buscar en ${label || 'esta sección'}...`}
          style={{ width: '100%', maxWidth: 460, padding: '11px 16px', borderRadius: 10, border: '1px solid #2a2a38', background: '#12121a', color: '#e8e8ed', fontSize: 15 }}
        />
      </div>

      <div className="kurz-grid" style={{ padding: 0 }}>
        {visibleItems.map((d, i) => {
          const imgSrc = d.poster_local ? '/' + d.poster_local : (d.poster?.startsWith('http') ? '/proxy/img?url=' + encodeURIComponent(d.poster) : (d.poster || ''));
          return (
            <div key={d.slug + '-' + i} className="kurz-card" onClick={() => handleOpen(d.slug)}>
              <div className="kurz-card-poster-wrap">
                {i < 3 && !q && <span className="card-tag" style={{ position: 'absolute', top: 6, left: 6, zIndex: 2 }}>Top {i + 1}</span>}
                {d.encrypted && <span className="card-tag drm" style={{ position: 'absolute', top: 6, right: 6, background: 'linear-gradient(135deg,#7c3aed,#a855f7)', zIndex: 2 }}>🔒 DRM</span>}
                {imgSrc ? (
                  <img 
                    src={imgSrc} 
                    alt={d.title} 
                    loading="lazy" 
                    decoding="async"
                    onError={(e) => {
                      e.currentTarget.style.display = 'none';
                      if (e.currentTarget.nextElementSibling && e.currentTarget.nextElementSibling.classList.contains('kurz-poster-fallback')) {
                        e.currentTarget.nextElementSibling.style.display = 'flex';
                      }
                    }}
                  />
                ) : null}
                <div className="kurz-poster-fallback" style={{ display: imgSrc ? 'none' : 'flex' }}>
                  <span>{d.title}</span>
                </div>
                <div className="kurz-play-overlay">
                  <div className="kurz-play-circle">
                    <svg viewBox="0 0 24 24" fill="white" width="22" height="22"><path d="M8 5v14l11-7z" /></svg>
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
        })}
      </div>

      <div ref={sentinelRef} style={{ height: 1 }} />

      {visibleCount < filteredItems.length && (
        <div style={{ textAlign: 'center', padding: 25, color: '#8a8a99' }}>
          <div className="spinner" style={{ margin: '0 auto 8px' }} />Cargando más títulos...
        </div>
      )}

      {filteredItems.length === 0 && (
        <div style={{ textAlign: 'center', padding: 60, color: '#8a8a99' }}>Sin resultados para &quot;{q}&quot;</div>
      )}

      <TitleModal slug={modalSlug} onClose={handleClose} />
    </>
  );
}
