'use client';
import { useState, useEffect, useRef } from 'react';

/**
 * Extractor inteligente de Slug y Episodio desde cualquier enlace o texto ingresado
 */
export function parseDramaUrl(input) {
  if (!input || typeof input !== 'string') return null;
  const clean = input.trim();

  // Caso 1: /ver/[slug]/[ep] o https://dramape.com/ver/[slug]/[ep]
  const mVer = clean.match(/\/ver\/([^\/\?#]+)(?:\/([^\/\?#]+))?/i);
  if (mVer) {
    return {
      slug: decodeURIComponent(mVer[1]),
      ep: mVer[2] ? decodeURIComponent(mVer[2]) : '1'
    };
  }

  // Caso 2: /titulo/[slug] o https://dramape.com/titulo/[slug]
  const mTit = clean.match(/\/titulo\/([^\/\?#]+)/i);
  if (mTit) {
    return {
      slug: decodeURIComponent(mTit[1]),
      ep: '1'
    };
  }

  // Caso 3: formato directo "slug/ep" o simplemente "slug"
  const cleanNoProto = clean.replace(/^https?:\/\/[^\/]+\/?/, '');
  const parts = cleanNoProto.split(/[/?#]/).filter(Boolean);
  if (parts.length >= 2) {
    const last = parts[parts.length - 1];
    const prev = parts[parts.length - 2];
    if (/^\d+$/.test(last) || /^\d+x\d+$/i.test(last)) {
      return { slug: prev, ep: last };
    }
  }
  if (parts.length === 1 && !clean.includes('.')) {
    return { slug: parts[0], ep: '1' };
  }

  return null;
}

export default function AdminVideoDownloader({ isOpen, onClose }) {
  const [urlInput, setUrlInput] = useState('');
  const [loadingInfo, setLoadingInfo] = useState(false);
  const [infoError, setInfoError] = useState('');
  const [episodeData, setEpisodeData] = useState(null); // { slug, ep, title, type, player_type, player_url }
  
  // Estado de descarga
  const [isDownloading, setIsDownloading] = useState(false);
  const [downloadFormat, setDownloadFormat] = useState('mp4'); // 'mp4' | 'ts'
  const [progress, setProgress] = useState({
    percent: 0,
    status: '',
    loadedMb: '0.0',
    currentSeg: 0,
    totalSegs: 0
  });
  const [downloadSuccess, setDownloadSuccess] = useState('');

  // Reproductor de vista previa
  const videoRef = useRef(null);
  const hlsRef = useRef(null);
  const [isPlayingPreview, setIsPlayingPreview] = useState(false);

  // Limpiar reproductor al cerrar o cambiar
  const cleanupPlayer = () => {
    if (hlsRef.current) {
      try {
        hlsRef.current.destroy();
      } catch (e) {}
      hlsRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.pause();
      videoRef.current.removeAttribute('src');
      videoRef.current.load();
    }
    setIsPlayingPreview(false);
  };

  useEffect(() => {
    if (!isOpen) {
      cleanupPlayer();
      setEpisodeData(null);
      setUrlInput('');
      setInfoError('');
      setDownloadSuccess('');
      setIsDownloading(false);
    }
  }, [isOpen]);

  // Manejar tecla Escape para cerrar
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isOpen && !isDownloading) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, isDownloading, onClose]);

  // Cargar stream en el video element de preview
  useEffect(() => {
    if (!episodeData || !episodeData.player_url || !isOpen) return;
    cleanupPlayer();

    const video = videoRef.current;
    if (!video) return;

    let cancelled = false;

    async function setupPreview() {
      const isHls = episodeData.player_type === 'hls' || episodeData.type === 'hls';
      const streamUrl = episodeData.player_url;

      if (!isHls) {
        video.src = streamUrl;
      } else {
        try {
          const Hls = (await import('hls.js')).default;
          if (Hls.isSupported()) {
            const hls = new Hls({
              enableWorker: true,
              lowLatencyMode: false,
              maxBufferLength: 10,
              maxMaxBufferLength: 20
            });
            hlsRef.current = hls;
            hls.loadSource(streamUrl);
            hls.attachMedia(video);
          } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
            video.src = streamUrl;
          }
        } catch (e) {
          console.error('Error cargando Hls preview:', e);
        }
      }
    }

    setupPreview();

    return () => {
      cancelled = true;
      cleanupPlayer();
    };
  }, [episodeData, isOpen]);

  // Buscar información del episodio
  const fetchEpisode = async (slug, ep) => {
    if (!slug) return;
    setLoadingInfo(true);
    setInfoError('');
    setDownloadSuccess('');
    cleanupPlayer();

    try {
      const epUrl = `/proxy/episode?slug=${encodeURIComponent(slug)}&ep=${encodeURIComponent(ep)}&fresh=1`;
      const res = await fetch(epUrl);
      if (!res.ok) {
        throw new Error(`Episodio no encontrado en el servidor (HTTP ${res.status})`);
      }
      const data = await res.json();
      if (data.encrypted) {
        throw new Error('Este video cuenta con cifrado DRM upstream y no puede ser extraído directamente.');
      }
      if (!data.player_url) {
        throw new Error('El episodio no devolvió una URL de video reproducible.');
      }

      setEpisodeData({
        slug,
        ep: String(ep),
        title: data.title || 'Dorama DramaPe',
        type: data.type || 'hls',
        player_type: data.player_type || 'hls',
        player_url: data.player_url,
        episode_number: data.episode_number || String(ep)
      });
    } catch (err) {
      setInfoError(err.message || 'Error al buscar el episodio');
      setEpisodeData(null);
    } finally {
      setLoadingInfo(false);
    }
  };

  const handleSearchSubmit = (e) => {
    if (e) e.preventDefault();
    if (!urlInput.trim()) return;

    const parsed = parseDramaUrl(urlInput);
    if (!parsed) {
      setInfoError('URL no reconocida. Pega un enlace como https://dramape.com/ver/slug/1');
      return;
    }
    fetchEpisode(parsed.slug, parsed.ep);
  };

  // Pegar directo desde el portapapeles
  const handlePasteClipboard = async () => {
    try {
      if (navigator?.clipboard?.readText) {
        const text = await navigator.clipboard.readText();
        if (text) {
          setUrlInput(text);
          const parsed = parseDramaUrl(text);
          if (parsed) {
            fetchEpisode(parsed.slug, parsed.ep);
          }
        }
      }
    } catch (e) {
      // Ignorar fallo de permisos
    }
  };

  // Navegar al capítulo anterior o siguiente sin re-pegar URLs
  const handleStepEpisode = (step) => {
    if (!episodeData) return;
    const currentNum = parseInt(episodeData.ep, 10);
    if (isNaN(currentNum)) return;
    const nextNum = Math.max(1, currentNum + step);
    fetchEpisode(episodeData.slug, nextNum);
  };

  // Motor de Descarga Concurrente de Video
  const handleDownloadVideo = async (formatOverride = null) => {
    if (!episodeData || isDownloading) return;
    const targetFormat = formatOverride || downloadFormat;
    setIsDownloading(true);
    setDownloadSuccess('');
    setInfoError('');

    setProgress({
      percent: 0,
      status: 'Conectando con la fuente de video...',
      loadedMb: '0.0',
      currentSeg: 0,
      totalSegs: 0
    });

    const isHls = episodeData.player_type === 'hls' || episodeData.type === 'hls';
    const cleanTitle = (episodeData.title || 'Dorama')
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/[^\w\s-]/gi, '')
      .trim()
      .replace(/\s+/g, '_');
    const fileName = `${cleanTitle}_Cap_${episodeData.ep}.${targetFormat}`;

    try {
      if (!isHls) {
        // === CASO DIRECTO MP4 ===
        setProgress({
          percent: 10,
          status: 'Descargando archivo directo MP4...',
          loadedMb: '0.0',
          currentSeg: 1,
          totalSegs: 1
        });

        const resp = await fetch(episodeData.player_url);
        if (!resp.ok) throw new Error(`Fallo HTTP ${resp.status} al descargar archivo.`);

        const reader = resp.body.getReader();
        const contentLength = +resp.headers.get('Content-Length') || 0;
        let received = 0;
        const chunks = [];

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          chunks.push(value);
          received += value.length;
          const mb = (received / (1024 * 1024)).toFixed(1);
          const pct = contentLength ? Math.min(99, Math.round((received / contentLength) * 100)) : 50;
          setProgress({
            percent: pct,
            status: `Descargando video (${mb} MB)...`,
            loadedMb: mb,
            currentSeg: 1,
            totalSegs: 1
          });
        }

        const blob = new Blob(chunks, { type: 'video/mp4' });
        triggerDownload(blob, fileName);

      } else {
        // === CASO HLS (.m3u8): DESCARGA PARALELA Y CONCATENACIÓN ===
        setProgress({
          percent: 5,
          status: 'Analizando lista de reproducción HLS...',
          loadedMb: '0.0',
          currentSeg: 0,
          totalSegs: 0
        });

        const mRes = await fetch(episodeData.player_url);
        if (!mRes.ok) throw new Error(`No se pudo leer la lista HLS (HTTP ${mRes.status})`);
        let mText = await mRes.text();

        // Si es master playlist con variantes, seleccionar la variante de mayor resolución
        const manifestLines = mText.split('\n').map(l => l.trim()).filter(Boolean);
        const subManifests = manifestLines.filter(l => l.startsWith('/proxy/manifest'));
        if (subManifests.length > 0) {
          const bestVariantUrl = subManifests[subManifests.length - 1];
          const subRes = await fetch(bestVariantUrl);
          if (subRes.ok) {
            mText = await subRes.text();
          }
        }

        // Extraer todos los segmentos /proxy/seg
        const segUrls = mText
          .split('\n')
          .map(l => l.trim())
          .filter(l => l && !l.startsWith('#') && (l.startsWith('/proxy/seg') || l.startsWith('http')));

        if (!segUrls.length) {
          throw new Error('La lista HLS no contiene segmentos válidos de video.');
        }

        const totalSegs = segUrls.length;
        const buffers = new Array(totalSegs);
        let completedCount = 0;
        let totalBytes = 0;

        setProgress({
          percent: 10,
          status: `Descargando ${totalSegs} fragmentos de video en paralelo...`,
          loadedMb: '0.0',
          currentSeg: 0,
          totalSegs
        });

        // Concurrencia de 4 descargas en paralelo para máxima velocidad sin saturar
        const CONCURRENCY = 4;
        let currentIdx = 0;

        const worker = async () => {
          while (currentIdx < totalSegs) {
            const idx = currentIdx++;
            const segUrl = segUrls[idx];
            
            let attempts = 0;
            let success = false;
            let lastErr = null;

            while (attempts < 3 && !success) {
              try {
                attempts++;
                const segRes = await fetch(segUrl);
                if (!segRes.ok) throw new Error(`HTTP ${segRes.status}`);
                const buf = await segRes.arrayBuffer();
                buffers[idx] = buf;
                totalBytes += buf.byteLength;
                completedCount++;
                success = true;

                const loadedMb = (totalBytes / (1024 * 1024)).toFixed(1);
                const pct = Math.min(98, Math.round((completedCount / totalSegs) * 90) + 10);
                setProgress({
                  percent: pct,
                  status: `Descargando fragmento ${completedCount}/${totalSegs} (${loadedMb} MB)...`,
                  loadedMb,
                  currentSeg: completedCount,
                  totalSegs
                });
              } catch (e) {
                lastErr = e;
                if (attempts < 3) {
                  await new Promise(r => setTimeout(r, 400));
                }
              }
            }

            if (!success) {
              throw new Error(`Fallo al descargar fragmento ${idx + 1}: ${lastErr?.message || 'error de red'}`);
            }
          }
        };

        const workers = Array.from({ length: Math.min(CONCURRENCY, totalSegs) }, () => worker());
        await Promise.all(workers);

        setProgress({
          percent: 99,
          status: 'Ensamblando archivo final listo para TikTok...',
          loadedMb: (totalBytes / (1024 * 1024)).toFixed(1),
          currentSeg: totalSegs,
          totalSegs
        });

        // Crear Blob con tipo correspondiente
        const mimeType = targetFormat === 'ts' ? 'video/mp2t' : 'video/mp4';
        const finalBlob = new Blob(buffers, { type: mimeType });
        triggerDownload(finalBlob, fileName);
      }

      setDownloadSuccess(`¡Descarga completada! Archivo: ${fileName}`);
      setProgress(p => ({ ...p, percent: 100, status: '¡Descarga finalizada con éxito! 🎉' }));
    } catch (err) {
      setInfoError(`Error durante la descarga: ${err.message || 'Fallo inesperado'}`);
    } finally {
      setIsDownloading(false);
    }
  };

  const triggerDownload = (blob, filename) => {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    setTimeout(() => {
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }, 60000);
  };

  const handleCopyDirectUrl = () => {
    if (!episodeData?.player_url) return;
    const fullUrl = window.location.origin + episodeData.player_url;
    navigator.clipboard.writeText(fullUrl).then(() => {
      alert('URL directa del stream copiada al portapapeles');
    }).catch(() => {});
  };

  if (!isOpen) return null;

  return (
    <div 
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 999999,
        backgroundColor: 'rgba(5, 5, 8, 0.88)',
        backdropFilter: 'blur(12px)',
        WebkitBackdropFilter: 'blur(12px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '16px',
        animation: 'fadeInModal 0.2s ease-out'
      }}
      onClick={(e) => {
        if (e.target === e.currentTarget && !isDownloading) onClose();
      }}
    >
      <div 
        style={{
          width: '100%',
          maxWidth: '680px',
          maxHeight: '90vh',
          backgroundColor: '#101017',
          border: '1px solid rgba(255, 255, 255, 0.12)',
          borderRadius: '16px',
          boxShadow: '0 24px 60px rgba(0, 0, 0, 0.8), 0 0 40px rgba(229, 9, 20, 0.15)',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          color: '#f4f4f5',
          fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
        }}
      >
        {/* ENCABEZADO DEL MODAL */}
        <div style={{
          padding: '18px 22px',
          borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          background: 'linear-gradient(180deg, rgba(229, 9, 20, 0.12) 0%, rgba(16, 16, 23, 0) 100%)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{
              background: '#e50914',
              color: '#fff',
              fontSize: '10px',
              fontWeight: '900',
              padding: '2px 7px',
              borderRadius: '4px',
              letterSpacing: '0.06em'
            }}>PRO</span>
            <div>
              <h2 style={{ margin: 0, fontSize: '16px', fontWeight: '800', letterSpacing: '-0.02em', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span>Descargador de Video</span>
                <span style={{ fontSize: '11px', color: '#10b981', background: 'rgba(16, 185, 129, 0.15)', padding: '2px 8px', borderRadius: '12px', fontWeight: '700' }}>
                  TikTok Edition ⚡
                </span>
              </h2>
              <p style={{ margin: '2px 0 0', fontSize: '12px', color: '#a1a1aa' }}>
                Descarga episodios limpios en alta definición para tus videos y reels
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            disabled={isDownloading}
            style={{
              background: 'rgba(255, 255, 255, 0.06)',
              border: 'none',
              color: '#a1a1aa',
              width: '32px',
              height: '32px',
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '18px',
              cursor: isDownloading ? 'not-allowed' : 'pointer',
              transition: 'all 0.15s ease'
            }}
            onMouseEnter={(e) => { if (!isDownloading) { e.currentTarget.style.color = '#fff'; e.currentTarget.style.background = 'rgba(255, 255, 255, 0.12)'; } }}
            onMouseLeave={(e) => { e.currentTarget.style.color = '#a1a1aa'; e.currentTarget.style.background = 'rgba(255, 255, 255, 0.06)'; }}
          >
            ✕
          </button>
        </div>

        {/* CONTENIDO PRINCIPAL CON SCROLL */}
        <div style={{ padding: '20px 22px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '18px' }}>
          
          {/* BARRA DE BÚSQUEDA Y URL */}
          <div>
            <label style={{ display: 'block', fontSize: '12px', fontWeight: '700', color: '#d4d4d8', marginBottom: '8px' }}>
              Pega el enlace del episodio a descargar:
            </label>
            <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: '8px' }}>
              <div style={{ position: 'relative', flex: 1 }}>
                <input
                  type="text"
                  placeholder="https://dramape.com/ver/dt-unida-al-alfa-y-su-beta-6a433648a0263ac457025610/3"
                  value={urlInput}
                  onChange={(e) => setUrlInput(e.target.value)}
                  disabled={isDownloading || loadingInfo}
                  style={{
                    width: '100%',
                    boxSizing: 'border-box',
                    padding: '11px 14px',
                    backgroundColor: '#181822',
                    border: '1px solid rgba(255, 255, 255, 0.12)',
                    borderRadius: '9px',
                    color: '#fff',
                    fontSize: '13px',
                    outline: 'none',
                    fontFamily: 'monospace'
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#e50914'}
                  onBlur={(e) => e.target.style.borderColor = 'rgba(255, 255, 255, 0.12)'}
                />
              </div>

              {/* Botón Pegar Portapapeles */}
              <button
                type="button"
                onClick={handlePasteClipboard}
                title="Pegar del portapapeles"
                disabled={isDownloading || loadingInfo}
                style={{
                  background: 'rgba(255, 255, 255, 0.06)',
                  border: '1px solid rgba(255, 255, 255, 0.12)',
                  color: '#e4e4e7',
                  padding: '0 14px',
                  borderRadius: '9px',
                  fontSize: '12px',
                  fontWeight: '700',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  whiteSpace: 'nowrap'
                }}
              >
                📋 Pegar
              </button>

              {/* Botón Buscar */}
              <button
                type="submit"
                disabled={isDownloading || loadingInfo || !urlInput.trim()}
                style={{
                  background: '#e50914',
                  border: 'none',
                  color: '#fff',
                  padding: '0 18px',
                  borderRadius: '9px',
                  fontSize: '13px',
                  fontWeight: '800',
                  cursor: (isDownloading || loadingInfo || !urlInput.trim()) ? 'not-allowed' : 'pointer',
                  opacity: (isDownloading || loadingInfo || !urlInput.trim()) ? 0.6 : 1,
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  whiteSpace: 'nowrap'
                }}
              >
                {loadingInfo ? 'Buscando...' : 'Buscar'}
              </button>
            </form>
            <div style={{ fontSize: '11px', color: '#71717a', marginTop: '6px' }}>
              💡 También puedes ingresar directamente el slug y capítulo (ejemplo: <span style={{ color: '#a1a1aa', fontFamily: 'monospace' }}>mi-esposo-hizo-rendirse-al-cielo/3</span>)
            </div>
          </div>

          {/* ALERTA DE ERROR */}
          {infoError && (
            <div style={{
              background: 'rgba(239, 68, 68, 0.12)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              borderRadius: '9px',
              padding: '12px 14px',
              color: '#f87171',
              fontSize: '12px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <span>⚠️</span>
              <span>{infoError}</span>
            </div>
          )}

          {/* TARJETA DEL EPISODIO ENCONTRADO */}
          {episodeData && (
            <div style={{
              background: '#15151e',
              border: '1px solid rgba(255, 255, 255, 0.09)',
              borderRadius: '12px',
              padding: '16px',
              display: 'flex',
              flexDirection: 'column',
              gap: '14px'
            }}>
              {/* TÍTULO Y NAVEGADOR DE CAPÍTULOS */}
              <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: '10px' }}>
                <div>
                  <h3 style={{ margin: 0, fontSize: '15px', fontWeight: '800', color: '#fff' }}>
                    {episodeData.title}
                  </h3>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '4px' }}>
                    <span style={{
                      background: 'rgba(229, 9, 20, 0.2)',
                      color: '#ff4d4d',
                      fontSize: '11px',
                      fontWeight: '800',
                      padding: '2px 8px',
                      borderRadius: '5px'
                    }}>
                      Capítulo {episodeData.ep}
                    </span>
                    <span style={{ fontSize: '11px', color: '#71717a' }}>•</span>
                    <span style={{ fontSize: '11px', color: '#a1a1aa' }}>
                      Formato: <strong style={{ color: '#38bdf8' }}>{episodeData.player_type.toUpperCase()}</strong>
                    </span>
                  </div>
                </div>

                {/* STEPPER DE CAPÍTULOS RÁPIDOS */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <button
                    type="button"
                    onClick={() => handleStepEpisode(-1)}
                    disabled={isDownloading || loadingInfo || parseInt(episodeData.ep, 10) <= 1}
                    style={{
                      background: 'rgba(255, 255, 255, 0.06)',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      color: '#d4d4d8',
                      padding: '5px 10px',
                      borderRadius: '6px',
                      fontSize: '11px',
                      fontWeight: '700',
                      cursor: (isDownloading || loadingInfo || parseInt(episodeData.ep, 10) <= 1) ? 'not-allowed' : 'pointer',
                      opacity: parseInt(episodeData.ep, 10) <= 1 ? 0.4 : 1
                    }}
                  >
                    ◀ Cap Anterior
                  </button>

                  <button
                    type="button"
                    onClick={() => handleStepEpisode(1)}
                    disabled={isDownloading || loadingInfo}
                    style={{
                      background: 'rgba(255, 255, 255, 0.06)',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      color: '#d4d4d8',
                      padding: '5px 10px',
                      borderRadius: '6px',
                      fontSize: '11px',
                      fontWeight: '700',
                      cursor: (isDownloading || loadingInfo) ? 'not-allowed' : 'pointer'
                    }}
                  >
                    Cap Siguiente ▶
                  </button>
                </div>
              </div>

              {/* REPRODUCTOR DE VISTA PREVIA (PARA VERIFICAR ANTES DE DESCARGAR) */}
              <div style={{
                position: 'relative',
                width: '100%',
                maxHeight: '260px',
                borderRadius: '8px',
                overflow: 'hidden',
                backgroundColor: '#000',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                border: '1px solid rgba(255, 255, 255, 0.06)'
              }}>
                <video
                  ref={videoRef}
                  controls
                  playsInline
                  style={{
                    maxHeight: '260px',
                    width: 'auto',
                    maxWidth: '100%',
                    display: 'block'
                  }}
                  onPlay={() => setIsPlayingPreview(true)}
                  onPause={() => setIsPlayingPreview(false)}
                />
              </div>

              {/* BARRA DE PROGRESO DE DESCARGA */}
              {isDownloading && (
                <div style={{
                  background: 'rgba(0, 0, 0, 0.4)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '10px',
                  padding: '12px 14px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '8px'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '12px' }}>
                    <span style={{ color: '#38bdf8', fontWeight: '700' }}>
                      {progress.status}
                    </span>
                    <span style={{ color: '#fff', fontWeight: '900', fontFamily: 'monospace' }}>
                      {progress.percent}%
                    </span>
                  </div>

                  {/* BARRA VISUAL */}
                  <div style={{
                    width: '100%',
                    height: '8px',
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    borderRadius: '4px',
                    overflow: 'hidden'
                  }}>
                    <div style={{
                      width: `${progress.percent}%`,
                      height: '100%',
                      backgroundColor: '#e50914',
                      background: 'linear-gradient(90deg, #e50914 0%, #ff4d4d 100%)',
                      transition: 'width 0.25s ease'
                    }} />
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: '#71717a' }}>
                    <span>
                      {progress.totalSegs > 0 ? `Fragmento ${progress.currentSeg} de ${progress.totalSegs}` : 'Descargando...'}
                    </span>
                    <span>{progress.loadedMb} MB descargados</span>
                  </div>
                </div>
              )}

              {/* MENSAJE DE ÉXITO */}
              {downloadSuccess && (
                <div style={{
                  background: 'rgba(16, 185, 129, 0.12)',
                  border: '1px solid rgba(16, 185, 129, 0.3)',
                  borderRadius: '9px',
                  padding: '10px 14px',
                  color: '#34d399',
                  fontSize: '12px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  <span>✅</span>
                  <span>{downloadSuccess}</span>
                </div>
              )}

              {/* BOTONES DE ACCIÓN Y DESCARGA */}
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '4px' }}>
                {/* BOTÓN PRINCIPAL: DESCARGAR MP4 */}
                <button
                  type="button"
                  onClick={() => handleDownloadVideo('mp4')}
                  disabled={isDownloading}
                  style={{
                    flex: 1,
                    minWidth: '200px',
                    background: '#e50914',
                    border: 'none',
                    color: '#fff',
                    padding: '12px 18px',
                    borderRadius: '9px',
                    fontSize: '13px',
                    fontWeight: '800',
                    cursor: isDownloading ? 'not-allowed' : 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '8px',
                    boxShadow: '0 4px 14px rgba(229, 9, 20, 0.35)',
                    transition: 'all 0.15s ease'
                  }}
                  onMouseEnter={(e) => { if (!isDownloading) e.currentTarget.style.backgroundColor = '#b80710'; }}
                  onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = '#e50914'; }}
                >
                  <span>⬇</span>
                  <span>{isDownloading ? 'Procesando descarga...' : `Descargar Video .MP4 (Capítulo ${episodeData.ep})`}</span>
                </button>

                {/* BOTÓN SECUNDARIO: DESCARGAR .TS NATIVO (PARA CAPCUT/PREMIERE) */}
                <button
                  type="button"
                  onClick={() => handleDownloadVideo('ts')}
                  disabled={isDownloading}
                  title="Descargar en formato nativo MPEG-TS para editores profesionales"
                  style={{
                    background: 'rgba(255, 255, 255, 0.06)',
                    border: '1px solid rgba(255, 255, 255, 0.12)',
                    color: '#d4d4d8',
                    padding: '12px 14px',
                    borderRadius: '9px',
                    fontSize: '12px',
                    fontWeight: '700',
                    cursor: isDownloading ? 'not-allowed' : 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px'
                  }}
                  onMouseEnter={(e) => { if (!isDownloading) e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.12)'; }}
                  onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.06)'; }}
                >
                  <span>🎞</span>
                  <span>Formato .TS</span>
                </button>

                {/* BOTÓN COPIAR ENLACE DIRECTO */}
                <button
                  type="button"
                  onClick={handleCopyDirectUrl}
                  disabled={isDownloading}
                  title="Copiar URL directa del manifest/stream"
                  style={{
                    background: 'rgba(255, 255, 255, 0.06)',
                    border: '1px solid rgba(255, 255, 255, 0.12)',
                    color: '#d4d4d8',
                    padding: '12px 14px',
                    borderRadius: '9px',
                    fontSize: '12px',
                    fontWeight: '700',
                    cursor: isDownloading ? 'not-allowed' : 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px'
                  }}
                >
                  <span>🔗</span>
                  <span>Copiar URL</span>
                </button>
              </div>

            </div>
          )}

        </div>

        {/* PIE DEL MODAL INFORMATIVO */}
        <div style={{
          padding: '12px 22px',
          borderTop: '1px solid rgba(255, 255, 255, 0.06)',
          backgroundColor: '#0c0c12',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          fontSize: '11px',
          color: '#71717a'
        }}>
          <span>🔐 Acceso Secreto Administrador</span>
          <span>DramaPe Studio • Calidad HD Vertical 9:16</span>
        </div>
      </div>
    </div>
  );
}
