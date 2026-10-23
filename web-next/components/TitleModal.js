'use client';
import { useEffect, useState, useRef, memo } from 'react';
import Link from 'next/link';
import { getDoramaProgress } from '../lib/watchHistory';
import ModalAdBanner from './ModalAdBanner';
import { checkAndTriggerPlayPopunder } from '../lib/adsterraAds';

// Cache global en memoria para persistir todos los títulos cargados
const modalCache = new Map();

function TitleModalComponent({ slug, onClose }) {
  const [d, setD] = useState(() => (slug && modalCache.has(slug) ? modalCache.get(slug) : null));
  const [err, setErr] = useState('');
  const [historyData, setHistoryData] = useState(null);
  const onCloseRef = useRef(onClose);

  useEffect(() => {
    if (slug) {
      setHistoryData(getDoramaProgress(slug));
    } else {
      setHistoryData(null);
    }
  }, [slug]);

  useEffect(() => {
    onCloseRef.current = onClose;
  }, [onClose]);

  // 1. Bloqueo de scroll y tecla Escape estable (sin re-ejecución innecesaria)
  useEffect(() => {
    if (!slug) return;
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';

    const onKey = (e) => {
      if (e.key === 'Escape' && onCloseRef.current) {
        onCloseRef.current();
      }
    };
    window.addEventListener('keydown', onKey);

    return () => {
      document.body.style.overflow = prevOverflow;
      window.removeEventListener('keydown', onKey);
    };
  }, [slug]);

  // 2. Carga de datos única por slug con cache persistente
  useEffect(() => {
    if (!slug) {
      setD(null);
      setErr('');
      return;
    }

    if (modalCache.has(slug)) {
      setD(modalCache.get(slug));
      setErr('');
      return;
    }

    let isCurrent = true;
    setErr('');

    fetch('/api/title/' + encodeURIComponent(slug))
      .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
      .then((data) => {
        if (isCurrent) {
          modalCache.set(slug, data);
          setD(data);
        }
      })
      .catch((e) => {
        if (isCurrent) setErr('No se pudo cargar el título (' + e + ')');
      });

    return () => {
      isCurrent = false;
    };
  }, [slug]);

  if (!slug) return null;

  const rawPoster = d ? (d.poster_local ? '/' + d.poster_local : d.poster) : '';
  const poster = rawPoster?.startsWith('http') ? '/proxy/img?url=' + encodeURIComponent(rawPoster) : rawPoster;

  return (
    <div
      className="modal-bg"
      onClick={(e) => {
        if (e.target === e.currentTarget && onCloseRef.current) {
          onCloseRef.current();
        }
      }}
    >
      <div className="modal">
        <div className="modal-hero">
          {poster ? (
            <img src={poster} alt={d ? d.title : ''} decoding="async" referrerPolicy="no-referrer" />
          ) : (
            d && <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(135deg,#1a1a24,#2a2a38)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#8a8a99', fontSize: 15, padding: 20, textAlign: 'center' }}>{d.title}</div>
          )}
          <button
            className="modal-close"
            onClick={() => onCloseRef.current && onCloseRef.current()}
            aria-label="Cerrar"
          >
            ✕
          </button>
          <div className="modal-hero-overlay">
            <h2 className="modal-title">{d ? d.title : 'Cargando…'}</h2>
            {d && (
              <div className="modal-actions" style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', alignItems: 'center' }}>
                {historyData?.last_ep ? (
                  <>
                    <Link
                      className="btn btn-play"
                      href={'/ver/' + d.slug + '/' + historyData.last_ep + (historyData.last_time > 3 ? `?t=${historyData.last_time}` : '')}
                      onClick={() => checkAndTriggerPlayPopunder()}
                    >
                      <svg viewBox="0 0 24 24" fill="currentColor" width="18" height="18" style={{ marginRight: 6 }}>
                        <path d="M8 5v14l11-7z" />
                      </svg>
                      Continuar Cap. {historyData.last_ep} {historyData.last_time > 3 ? `(${Math.floor(historyData.last_time / 60)}:${Math.floor(historyData.last_time % 60) < 10 ? '0' : ''}${Math.floor(historyData.last_time % 60)})` : ''}
                    </Link>
                    <Link
                      className="btn"
                      href={'/ver/' + d.slug + '/1'}
                      onClick={() => checkAndTriggerPlayPopunder()}
                      style={{
                        background: 'rgba(255, 255, 255, 0.12)',
                        color: '#f4f4f5',
                        border: '1px solid rgba(255, 255, 255, 0.18)',
                        display: 'inline-flex',
                        alignItems: 'center',
                        fontSize: '13px',
                        fontWeight: '600',
                        padding: '8px 14px',
                        borderRadius: '6px'
                      }}
                    >
                      Desde el Cap. 1
                    </Link>
                  </>
                ) : (
                  <Link 
                    className="btn btn-play" 
                    href={'/ver/' + d.slug + '/1'}
                    onClick={() => checkAndTriggerPlayPopunder()}
                  >
                    <svg viewBox="0 0 24 24" fill="currentColor" width="18" height="18" style={{ marginRight: 6 }}>
                      <path d="M8 5v14l11-7z" />
                    </svg>
                    Reproducir
                  </Link>
                )}
              </div>
            )}
          </div>
        </div>

        <div className="modal-body">
          <div>
            {err && <p className="modal-desc" style={{ color: '#ff6b6b' }}>{err}</p>}
            {d ? (
              <>
                <div className="modal-meta-row">
                  <div className="modal-meta-item">
                    <span className="k">Episodios</span>
                    <span className="v">{d.total_episodes}</span>
                  </div>
                  <div className="modal-meta-item">
                    <span className="k">Género</span>
                    <span className="v">{(d.genres || []).join(' · ') || 'Drama'}</span>
                  </div>
                  <div className="modal-meta-item">
                    <span className="k">Año</span>
                    <span className="v">2026</span>
                  </div>
                  <div className="modal-meta-item">
                    <span className="k">Idioma</span>
                    <span className="v">{d.lang === 'en' ? 'Inglés' : 'Español'}</span>
                  </div>
                </div>
                <p className="modal-desc">{d.description}</p>

                {/* Banner Adsterra Adaptable (300x250 en desktop, 320x50 en móviles/tablets) */}
                <ModalAdBanner />
              </>
            ) : !err ? (
              <div style={{ color: 'var(--muted)', padding: '20px 0' }}>Cargando información del drama...</div>
            ) : null}
          </div>

          <div>
            {d && (
              <>
                <div className="episodes-title">📺 Episodios ({d.total_episodes})</div>
                <div className="episodes-grid">
                  {(d.episodeKeys || []).map((k) => {
                    const kStr = String(k).trim();
                    const isWatched = historyData?.vistos && historyData.vistos.some(v => String(v).trim() === kStr);
                    const isLast = historyData?.last_ep && String(historyData.last_ep).trim() === kStr;
                    const label = kStr.includes('x')
                      ? ('T' + kStr.split('x')[0] + ' E' + kStr.split('x')[1])
                      : ('EP ' + kStr);

                    return (
                      <Link
                        key={k}
                        className={`ep-btn ${isLast ? 'ep-last-watched' : (isWatched ? 'ep-watched' : '')}`}
                        href={'/ver/' + d.slug + '/' + k}
                        onClick={() => checkAndTriggerPlayPopunder()}
                      >
                        {isWatched && <span className="ep-check-icon">✓</span>}
                        <span>{label}</span>
                      </Link>
                    );
                  })}
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

const TitleModal = memo(TitleModalComponent);
export default TitleModal;

