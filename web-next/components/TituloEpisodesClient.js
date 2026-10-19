'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { getDoramaProgress } from '../lib/watchHistory';

export default function TituloEpisodesClient({ slug, total, eps }) {
  const [historyData, setHistoryData] = useState(null);

  useEffect(() => {
    if (slug) {
      setHistoryData(getDoramaProgress(slug));
    }
  }, [slug]);

  return (
    <div style={{ marginTop: '20px' }}>
      {/* Botón de acción principal (Continuar o Reproducir) */}
      <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', marginBottom: '24px' }}>
        {historyData?.last_ep ? (
          <>
            <Link
              className="btn btn-play"
              href={'/ver/' + slug + '/' + historyData.last_ep}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                background: '#e50914',
                color: '#fff',
                padding: '10px 22px',
                borderRadius: '8px',
                fontWeight: '700',
                fontSize: '15px',
                textDecoration: 'none',
                boxShadow: '0 4px 16px rgba(229, 9, 20, 0.4)'
              }}
            >
              <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
                <path d="M8 5v14l11-7z" />
              </svg>
              Continuar viendo (Cap. {historyData.last_ep})
            </Link>
            <Link
              className="btn"
              href={'/ver/' + slug + '/1'}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                background: 'rgba(255, 255, 255, 0.1)',
                color: '#e4e4e7',
                border: '1px solid rgba(255, 255, 255, 0.15)',
                padding: '10px 18px',
                borderRadius: '8px',
                fontWeight: '600',
                fontSize: '14px',
                textDecoration: 'none'
              }}
            >
              Desde el Cap. 1
            </Link>
          </>
        ) : (
          <Link
            className="btn btn-play"
            href={'/ver/' + slug + '/1'}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              background: '#e50914',
              color: '#fff',
              padding: '10px 22px',
              borderRadius: '8px',
              fontWeight: '700',
              fontSize: '15px',
              textDecoration: 'none',
              boxShadow: '0 4px 16px rgba(229, 9, 20, 0.4)'
            }}
          >
            <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
              <path d="M8 5v14l11-7z" />
            </svg>
            Reproducir desde el Cap. 1
          </Link>
        )}
      </div>

      <h2 style={{ fontSize: 18, marginBottom: 12, display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span>📺</span>
        <span>Episodios ({total})</span>
        {historyData?.vistos?.length > 0 && (
          <span style={{ fontSize: '12px', color: '#10b981', fontWeight: 'normal', background: 'rgba(16, 185, 129, 0.12)', padding: '2px 8px', borderRadius: '10px' }}>
            {historyData.vistos.length} vistos
          </span>
        )}
      </h2>

      <div className="ep-grid">
        {(eps || []).map((key) => {
          const kStr = String(key).trim();
          const isWatched = historyData?.vistos && historyData.vistos.some(v => String(v).trim() === kStr);
          const isLast = historyData?.last_ep && String(historyData.last_ep).trim() === kStr;
          const label = kStr.includes('x')
            ? ('T' + kStr.split('x')[0] + ' E' + kStr.split('x')[1])
            : ('EP ' + kStr);

          return (
            <Link
              key={key}
              className={`ep-btn ${isLast ? 'ep-last-watched' : (isWatched ? 'ep-watched' : '')}`}
              href={'/ver/' + slug + '/' + key}
            >
              {isWatched && <span className="ep-check-icon">✓</span>}
              <span>{label}</span>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
