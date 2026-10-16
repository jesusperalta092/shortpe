'use client';
import { useState, useCallback, useEffect, useMemo, useRef } from 'react';
import { useSearchParams } from 'next/navigation';
import Carousel from './Carousel';
import TitleModal from './TitleModal';

export default function DramaTubeClient({ shelves = [], allDramas = [], totalCount = 122 }) {
  const [modalSlug, setModalSlug] = useState(null);
  const [activeShelf, setActiveShelf] = useState('all');
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [viewMode, setViewMode] = useState('shelves'); // 'shelves' | 'grid'
  const [q, setQ] = useState('');
  const searchParams = useSearchParams();
  const shelfRefs = useRef({});
  const pillsRef = useRef(null);

  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(true);

  const checkPillsScroll = useCallback(() => {
    const el = pillsRef.current;
    if (!el) return;
    const { scrollLeft, scrollWidth, clientWidth } = el;
    setCanScrollLeft(scrollLeft > 10);
    setCanScrollRight(scrollLeft + clientWidth < scrollWidth - 10);
  }, []);

  const scrollPills = (direction) => {
    const el = pillsRef.current;
    if (el) {
      el.scrollBy({ left: direction * 280, behavior: 'smooth' });
      setTimeout(checkPillsScroll, 350);
    }
  };

  useEffect(() => {
    checkPillsScroll();
    const handleResize = () => checkPillsScroll();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [checkPillsScroll]);

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

  // Filtrado por buscador general
  const filteredDramas = useMemo(() => {
    if (!q.trim()) return allDramas;
    const query = q.toLowerCase().trim();
    return allDramas.filter(d => 
      (d.title && d.title.toLowerCase().includes(query)) ||
      (d.shelf && d.shelf.toLowerCase().includes(query))
    );
  }, [allDramas, q]);

  // Filtrado por estantes en modo carrusel
  const visibleShelves = useMemo(() => {
    if (q.trim()) {
      const query = q.toLowerCase().trim();
      return shelves.map(sh => {
        const fullList = sh.all_items || sh.items || [];
        const filtered = fullList.filter(it => it.title && it.title.toLowerCase().includes(query));
        return {
          ...sh,
          items: filtered.slice(0, 10),
          all_items: filtered,
          count: filtered.length
        };
      }).filter(sh => sh.items.length > 0);
    }
    return shelves;
  }, [shelves, q]);

  // Selección de categoría desde los botones superiores (Pills)
  const selectShelf = (shelfName) => {
    if (shelfName === 'all') {
      setActiveShelf('all');
      setSelectedCategory(null);
      return;
    }
    const sh = shelves.find(s => s.name === shelfName || s.slug === shelfName);
    if (sh) {
      setActiveShelf(sh.name);
      setSelectedCategory(sh);
      if (typeof window !== 'undefined') {
        window.scrollTo({ top: 180, behavior: 'smooth' });
      }
    }
  };

  // Abrir vista expandida de una categoría (desde el botón o tarjeta "+ Más")
  const handleOpenCategory = (sh) => {
    setSelectedCategory(sh);
    setActiveShelf(sh.name);
    if (typeof window !== 'undefined') {
      window.scrollTo({ top: 180, behavior: 'smooth' });
    }
  };

  // Volver a la vista general de todos los carruseles
  const handleBackToAll = () => {
    setSelectedCategory(null);
    setActiveShelf('all');
  };

  // Items mostrados en la vista de categoría expandida
  const categoryItems = useMemo(() => {
    if (!selectedCategory) return [];
    const list = selectedCategory.all_items || selectedCategory.items || [];
    if (!q.trim()) return list;
    const query = q.toLowerCase().trim();
    return list.filter(d => d.title && d.title.toLowerCase().includes(query));
  }, [selectedCategory, q]);

  const effectiveTotal = totalCount || allDramas.length || 122;

  return (
    <div className="dramatube-container">
      {/* Header Info y Buscador */}
      <div className="dramatube-hero-header">
        <div className="dramatube-hero-badge">
          <span className="dot" /> 🔴 EXCLUSIVO EN DRAMATUBE
        </div>
        <h1 className="dramatube-title">
          Drama<span className="text-red">Tube</span>
        </h1>
        <p className="dramatube-subtitle">
          Disfruta de las mejores series cortas y doramas en español organizados por categorías temáticas exclusivas. {effectiveTotal} títulos disponibles en audio español latino y calidad HD.
        </p>

        {/* Buscador y Controles de Vista */}
        <div className="dramatube-controls">
          <div className="dramatube-search-box">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
            </svg>
            <input 
              type="text" 
              placeholder={selectedCategory ? `Buscar en ${selectedCategory.name}...` : "Buscar título o categoría en DramaTube..."}
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
              className={`view-btn ${viewMode === 'shelves' && !selectedCategory ? 'active' : ''}`}
              onClick={() => { setViewMode('shelves'); setSelectedCategory(null); }}
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
              onClick={() => { setViewMode('grid'); setSelectedCategory(null); }}
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

        {/* Barra de Filtros de Secciones con Flechas Deslizantes */}
        <div className="dramatube-pills-container">
          {canScrollLeft && (
            <button 
              className="dramatube-pills-arrow left" 
              onClick={() => scrollPills(-1)} 
              aria-label="Deslizar categorías a la izquierda"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.8">
                <polyline points="15 18 9 12 15 6" />
              </svg>
            </button>
          )}

          <div 
            className="dramatube-pills-scroll" 
            ref={pillsRef}
            onScroll={checkPillsScroll}
          >
            <button 
              className={`dramatube-pill ${activeShelf === 'all' && !selectedCategory ? 'active' : ''}`}
              onClick={() => selectShelf('all')}
            >
              <span>Todos</span>
              <span className="pill-badge">{effectiveTotal}</span>
            </button>
            {shelves.map((sh) => {
              const isSelected = selectedCategory ? (selectedCategory.name === sh.name) : (activeShelf === sh.name);
              const totalInShelf = sh.all_items ? sh.all_items.length : (sh.count || sh.items.length);
              return (
                <button 
                  key={sh.name}
                  className={`dramatube-pill ${isSelected ? 'active' : ''}`}
                  onClick={() => selectShelf(sh.name)}
                >
                  <span className="pill-icon">{sh.icon}</span>
                  <span>{sh.name}</span>
                  <span className="pill-badge">{totalInShelf}</span>
                </button>
              );
            })}
          </div>

          {canScrollRight && (
            <button 
              className="dramatube-pills-arrow right" 
              onClick={() => scrollPills(1)} 
              aria-label="Deslizar categorías a la derecha"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.8">
                <polyline points="9 18 15 12 9 6" />
              </svg>
            </button>
          )}
        </div>
      </div>

      {/* Contenido según vista seleccionada */}
      {selectedCategory ? (
        /* Vista de Categoría Expandida (al hacer click en "Más +" o en una categoría) */
        <div className="dramatube-category-view">
          <div className="dramatube-cat-header">
            <button className="dramatube-back-btn" onClick={handleBackToAll}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <line x1="19" y1="12" x2="5" y2="12" />
                <polyline points="12 19 5 12 12 5" />
              </svg>
              <span>Volver a todas las secciones</span>
            </button>

            <div className="dramatube-cat-title-wrap">
              <span className="dramatube-cat-icon">{selectedCategory.icon}</span>
              <h2 className="dramatube-cat-title">{selectedCategory.name}</h2>
              <span className="dramatube-cat-badge">
                {categoryItems.length} {categoryItems.length === 1 ? 'título' : 'títulos'}
              </span>
            </div>
            <p className="dramatube-cat-desc">
              Catálogo completo de {selectedCategory.name} en audio español latino y calidad HD.
            </p>
          </div>

          {categoryItems.length === 0 ? (
            <div className="dramatube-empty">
              <p>No se encontraron títulos en esta categoría con &quot;{q}&quot;.</p>
              <button className="dramatube-reset-btn" onClick={() => setQ('')}>
                Limpiar búsqueda
              </button>
            </div>
          ) : (
            <div className="kurz-grid">
              {categoryItems.map((d, i) => (
                <div 
                  key={d.slug + '-' + i} 
                  className="kurz-card" 
                  onClick={() => handleOpenModal(d.slug)}
                >
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
                        <svg viewBox="0 0 24 24" fill="white" width="22" height="22">
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
              ))}
            </div>
          )}
        </div>
      ) : viewMode === 'shelves' ? (
        /* Vista de Secciones con Carruseles Kurzdrama */
        <div className="dramatube-shelves-list">
          {visibleShelves.length === 0 ? (
            <div className="dramatube-empty">
              <p>No se encontraron títulos en esta búsqueda.</p>
              <button className="dramatube-reset-btn" onClick={() => setQ('')}>
                Limpiar búsqueda
              </button>
            </div>
          ) : (
            visibleShelves.map((sh) => {
              const totalInShelf = sh.all_items ? sh.all_items.length : (sh.count || sh.items.length);
              const itemsToShow = (sh.items || []).slice(0, 10);
              const remaining = Math.max(0, totalInShelf - itemsToShow.length);

              return (
                <div 
                  key={sh.name} 
                  ref={(el) => (shelfRefs.current[sh.name] = el)}
                  className="dramatube-shelf-block"
                >
                  <div className="dramatube-shelf-header">
                    <div className="dramatube-shelf-header-left">
                      <span className="shelf-icon">{sh.icon}</span>
                      <h2 className="dramatube-shelf-title">{sh.name}</h2>
                      <span className="shelf-count">({totalInShelf})</span>
                    </div>
                    {totalInShelf > 10 && (
                      <button 
                        className="dramatube-shelf-more-btn"
                        onClick={() => handleOpenCategory(sh)}
                        title={`Ver todos los ${totalInShelf} títulos de ${sh.name}`}
                      >
                        <span>Ver más + ({totalInShelf})</span>
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                          <path d="m9 18 6-6-6-6"/>
                        </svg>
                      </button>
                    )}
                  </div>
                  <Carousel 
                    title="" 
                    variant="kurzdrama"
                    items={itemsToShow} 
                    onOpen={handleOpenModal} 
                    onMore={totalInShelf > 10 ? () => handleOpenCategory(sh) : null}
                    moreLabel="Más +"
                    totalCount={totalInShelf}
                    remainingCount={remaining}
                  />
                </div>
              );
            })
          )}
        </div>
      ) : (
        /* Vista en Cuadrícula Completa de todos los dramas */
        <div className="dramatube-grid-view">
          <div className="kurz-grid">
            {filteredDramas.map((d, i) => (
              <div 
                key={d.slug + '-' + i} 
                className="kurz-card" 
                onClick={() => handleOpenModal(d.slug)}
              >
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
                      <svg viewBox="0 0 24 24" fill="white" width="22" height="22">
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
            ))}
          </div>
        </div>
      )}

      <TitleModal slug={modalSlug} onClose={handleCloseModal} />
    </div>
  );
}
