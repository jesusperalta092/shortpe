'use client';
import { useRef } from 'react';

export default function Carousel({ title, items, onOpen }) {
  const trackRef = useRef(null);
  if (!items || !items.length) return null;
  const scroll = (dir) => {
    const t = trackRef.current;
    if (t) t.scrollBy({ left: dir * (t.clientWidth * 0.8), behavior: 'smooth' });
  };
  return (
    <section className="row">
      <h2 className="row-title"><span className="bar" />{title}</h2>
      <div className="carousel">
        <button className="nav-arrow left" onClick={() => scroll(-1)} aria-label="Anterior">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="m15 18-6-6 6-6" /></svg>
        </button>
        <button className="nav-arrow right" onClick={() => scroll(1)} aria-label="Siguiente">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="m9 18 6-6-6-6" /></svg>
        </button>
        <div className="carousel-track" ref={trackRef}>
          {items.map((d, i) => (
            <div key={d.slug + '-' + i} className="card" onClick={() => onOpen && onOpen(d.slug)}>
              {i < 3 && <div className="card-tag new">TOP {i + 1}</div>}
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
          ))}
        </div>
      </div>
    </section>
  );
}
