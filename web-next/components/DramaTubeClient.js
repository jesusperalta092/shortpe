'use client';
import { useState, useCallback, useEffect, useMemo, useRef } from 'react';
import { useSearchParams } from 'next/navigation';
import Carousel from './Carousel';
import TitleModal from './TitleModal';

export default function DramaTubeClient({ shelves = [], allDramas = [], totalCount = 114 }) {
  const [modalSlug, setModalSlug] = useState(null);
  const [activeShelf, setActiveShelf] = useState('all');
  const [viewMode, setViewMode] = useState('shelves'); // 'shelves' | 'grid'
  const [q, setQ] = useState('');
  const searchParams = useSearchParams();
  const shelfRefs = useRef({});

  useEffect(() => {
    if (typeof window !== 'undefined') {
      sessionStorage.setItem('dramia_last_section', window.location.pathname + window.location.search);
    }
  }, []);

  // Si llega con ?open=slug (al volver del player), abrir el modal
  useEffect(() => {
    const open = searchParams.get('open');
    if (open) setModalSlug(open);
  }, [searchParams]);

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

  // Filtrado por buscador
  const filteredDramas = useMemo(() => {
    if (!q.trim()) return allDramas;
    const query = q.toLowerCase().trim();
    return allDramas.filter(d => 
      (d.title && d.title.toLowerCase().includes(query)) ||
      (d.shelf && d.shelf.toLowerCase().includes(query))
    );
  }, [allDramas, q]);

  // Filtrado por estantes
  const visibleShelves = useMemo(() => {
    if (q.trim()) {
      // Filtrar items dentro de cada shelf segun la busqueda
      const query = q.toLowerCase().trim();
      return shelves.map(sh => ({
        ...sh,
        items: sh.items.filter(it => it.title && it.title.toLowerCase().includes(query))
      })).filter(sh => sh.items.length > 0);
    }
    if (activeShelf === 'all') {
      return shelves;
    }
    return shelves.filter(sh => sh.name === activeShelf || sh.slug === activeShelf);
  }, [shelves, activeShelf, q]);

  const selectShelf = (shelfName) => {
    setActiveShelf(shelfName);
    if (viewMode === 'shelves' && shelfName !== 'all') {
      const el = shelfRefs.current[shelfName];
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }
  };

  return (
    <div className="dramatube-container">
      {/* Banner de Seccion DramaTube */}
      <div className="dramatube-hero-header">
        <div className="dramatube-hero-badge">
          <span className="dot" /> 🔴 EXCLUSIVO EN DRAMATUBE
        </div>
        <h1 className="dramatube-title">
          Drama<span className="text-red">Tube</span>
        </h1>
        <p className="dramatube-subtitle">
          Disfruta de las mejores series cortas y doramas en español organizados por categorías temáticas exclusivas. {totalCount} títulos en audio español latino y HD.
        </p>

        {/* Buscador y Controles de Vista */}
        <div className="dramatube-controls">
          <div className="dramatube-search-box">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
            </svg>
            <input 
              type="text" 
              placeholder="Buscar título o categoría en DramaTube..." 
              value={q}
              onChange={(e) => setQ(e.target.value)}
              className="dramatube-search-input"
            />
            {q && (
              <button className="dramatube-search-clear" onClick={() => setQ('')} aria-label="Limpiar búsqueda">✕</button>
            )}
          </div>

          <div className="dramatube-view-toggle">
            <button 
              className={`view-btn ${viewMode === 'shelves' ? 'active' : ''}`}
              onClick={() => setViewMode('shelves')}
              title="Ver por Secciones temáticas"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                <line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/>
                <line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/>
              </svg>
              <span>Secciones</span>
            </button>
            <button 
              className={`view-btn ${viewMode === 'grid' ? 'active' : ''}`}
              onClick={() => setViewMode('grid')}
              title="Ver todos en Cuadrícula"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                <rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/>
                <rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>
              </svg>
              <span>Cuadrícula</span>
            </button>
          </div>
        </div>

        {/* Barra de Filtros de Secciones (Pills) */}
        <div className="dramatube-pills-scroll">
          <button 
            className={`dramatube-pill ${activeShelf === 'all' ? 'active' : ''}`}
            onClick={() => selectShelf('all')}
          >
            <span>Todos</span>
            <span className="pill-badge">{totalCount}</span>
          </button>
          {shelves.map((sh) => (
            <button 
              key={sh.name}
              className={`dramatube-pill ${activeShelf === sh.name ? 'active' : ''}`}
              onClick={() => selectShelf(sh.name)}
            >
              <span className="pill-icon">{sh.icon}</span>
              <span>{sh.name}</span>
              <span className="pill-badge">{sh.count}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Contenido: Vista por Secciones / Shelves */}
      {viewMode === 'shelves' ? (
        <div className="dramatube-shelves-list">
          {visibleShelves.length === 0 ? (
            <div className="dramatube-empty">
              <p>No se encontraron títulos en esta búsqueda.</p>
            </div>
          ) : (
            visibleShelves.map((sh) => (
              <div 
                key={sh.name} 
                ref={(el) => (shelfRefs.current[sh.name] = el)}
                className="dramatube-shelf-block"
              >
                <div className="dramatube-shelf-header">
                  <h2 className="dramatube-shelf-title">
                    <span className="shelf-bar" />
                    <span className="shelf-icon">{sh.icon}</span>
                    <span>{sh.name}</span>
                    <span className="shelf-count">({sh.items.length})</span>
                  </h2>
                </div>
                <Carousel 
                  title="" 
                  items={sh.items} 
                  onOpen={handleOpenModal} 
                />
              </div>
            ))
          )}
        </div>
      ) : (
        /* Vista en Cuadrícula Completa */
        <div className="dramatube-grid-view">
          <div className="grid">
            {filteredDramas.map((d, i) => (
              <div 
                key={d.slug + '-' + i} 
                className="card" 
                onClick={() => handleOpenModal(d.slug)}
              >
                {i < 3 && <div className="card-tag new">TOP {i + 1}</div>}
                <img 
                  src={d.poster_local ? '/' + d.poster_local : (d.poster?.startsWith('http') ? '/proxy/img?url=' + encodeURIComponent(d.poster) : (d.poster || '/favicon.ico'))} 
                  alt={d.title} 
                  loading="lazy" 
                  onError={(e) => {
                    e.currentTarget.style.display = 'none';
                    if (e.currentTarget.nextElementSibling) {
                      e.currentTarget.nextElementSibling.style.display = 'flex';
                    }
                  }}
                />
                <div className="card-poster-fallback" style={{ display: d.poster ? 'none' : 'flex' }}>
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
            ))}
          </div>
        </div>
      )}

      <TitleModal slug={modalSlug} onClose={handleCloseModal} />
    </div>
  );
}
