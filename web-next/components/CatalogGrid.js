'use client';
import { useState, useEffect, useRef, useCallback } from 'react';
import { useSearchParams } from 'next/navigation';
import TitleModal from './TitleModal';

const PAGE = 48;

/**
 * Grid generico para secciones con catalogo grande (DramaVibe, HotDrama).
 * Props:
 *   initial: {items, total, page, pages}
 *   apiPath: '/api/dramavibe' o '/api/hotdrama'
 *   label: nombre para el buscador
 *   fireTag: si true, las 3 primeras cards llevan tag "FIRE"
 */
export default function CatalogGrid({ initial, apiPath, label = 'Catalogo', fireTag = false }) {
  const [items, setItems] = useState(initial?.items || []);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(initial?.total || 0);
  const [pages, setPages] = useState(initial?.pages || 1);
  const [loading, setLoading] = useState(false);
  const [q, setQ] = useState('');
  const [query, setQuery] = useState('');
  const [modalSlug, setModalSlug] = useState(null);
  const sentinel = useRef(null);
  const loadingRef = useRef(false);
  const searchParams = useSearchParams();

  const loadPage = useCallback(async (p, queryStr, replace) => {
    if (loadingRef.current) return;
    loadingRef.current = true;
    setLoading(true);
    try {
      const url = apiPath + `?page=${p}&limit=${PAGE}` + (queryStr ? '&q=' + encodeURIComponent(queryStr) : '');
      const r = await fetch(url, { cache: 'no-store' });
      if (r.ok) {
        const d = await r.json();
        setItems((prev) => {
          if (replace) return d.items || [];
          const seenSlugs = new Set(prev.map(item => item.slug));
          const newItems = (d.items || []).filter(item => !seenSlugs.has(item.slug));
          return [...prev, ...newItems];
        });
        setTotal(d.total);
        setPages(d.pages);
        setPage(d.page);
      }
    } catch (e) {}
    loadingRef.current = false;
    setLoading(false);
  }, [apiPath]);

  useEffect(() => {
    const el = sentinel.current;
    if (!el) return;
    const io = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting && !loadingRef.current && page < pages) {
        loadPage(page + 1, query, false);
      }
    }, { rootMargin: '400px' });
    io.observe(el);
    return () => io.disconnect();
  }, [page, pages, query, loadPage]);

  useEffect(() => {
    const t = setTimeout(() => {
      if (q !== query) {
        setQuery(q);
        loadPage(1, q, true);
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    }, 500);
    return () => clearTimeout(t);
  }, [q]);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      sessionStorage.setItem('dramia_last_section', window.location.pathname + window.location.search);
    }
  }, []);

  // Si llega con ?open=slug (al volver del player), abrir el modal
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

  const card = (d, i) => (
    <div key={d.slug + '-' + i} className="card" onClick={() => handleOpen(d.slug)}>
      {fireTag && i < 3 && page === 1 && !query && (
        <span className="card-tag fire">🔥 HOT {i + 1}</span>
      )}
      {!fireTag && i < 3 && page === 1 && !query && (
        <span className="card-tag">Top {i + 1}</span>
      )}
      {(d.poster_local || d.poster) ? (
        <img 
          src={d.poster_local ? '/' + d.poster_local : (d.poster?.startsWith('http') ? '/proxy/img?url=' + encodeURIComponent(d.poster) : d.poster)} 
          alt={d.title} 
          loading="lazy" 
          decoding="async" 
        />
      ) : (
        <div className="card-noimg" style={{ position: 'absolute', inset: 0, background: 'linear-gradient(135deg,#1a1a24,#2a2a38)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#8a8a99', fontSize: 13, textAlign: 'center', padding: 10 }}>{d.title}</div>
      )}
      <div className="card-play"><svg viewBox="0 0 24 24" fill="white"><path d="M8 5v14l11-7z" /></svg></div>
      <div className="card-overlay">
        <div className="card-title">{d.title}</div>
        <div className="card-overlay-meta"><span className="match">98%</span><span className="pill">+16</span><span>{d.total_episodes || '?'} eps</span></div>
      </div>
    </div>
  );

  return (
    <>
      <div className="dv-search-wrap" style={{ marginBottom: 18 }}>
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder={'Buscar en ' + label + '...'}
          style={{ width: '100%', maxWidth: 460, padding: '11px 16px', borderRadius: 10, border: '1px solid #2a2a38', background: '#12121a', color: '#e8e8ed', fontSize: 15 }}
        />
      </div>

      <div className="grid" style={{ padding: 0 }}>
        {items.map(card)}
      </div>

      {loading && (
        <div style={{ textAlign: 'center', padding: 30, color: '#8a8a99' }}>
          <div className="spinner" style={{ margin: '0 auto 10px' }} />Cargando más...
        </div>
      )}

      <div ref={sentinel} style={{ height: 1 }} />

      {!loading && page >= pages && items.length > 0 && (
        <div style={{ textAlign: 'center', padding: 24, color: '#8a8a99', fontSize: 13 }}>
          Mostrando {items.length.toLocaleString('es')} de {total.toLocaleString('es')}
        </div>
      )}

      {!loading && items.length === 0 && (
        <div style={{ textAlign: 'center', padding: 60, color: '#8a8a99' }}>Sin resultados para &quot;{query}&quot;</div>
      )}

      <TitleModal slug={modalSlug} onClose={handleClose} />
    </>
  );
}
