'use client';
import { useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { trackVideoPlay, trackAdClick, trackLiveHeartbeat, reportVideoError } from '../lib/analytics';

export const AD_LINKS_ROTATION = [
  'https://asiafilm.org/4/422780c437bf41678b7ed041ce2360a0', // 1. Adsterra
  'https://omg10.com/4/11963834',                             // 2. Monetag
  'https://asiafilm.org/4/422780c437bf41678b7ed041ce2360a0', // 3. Adsterra
  'https://omg10.com/4/11963834'                              // 4. Monetag
];
export const AD_LINK = AD_LINKS_ROTATION[0];
export const REQUIRED_AD_CLICKS = AD_LINKS_ROTATION.length;

export function isEpisodeAdRestricted(ep) {
  const s = String(ep || '1');
  if (s.includes('x')) {
    const parts = s.split('x');
    const epNum = parseInt(parts[1], 10);
    return !isNaN(epNum) && epNum >= 5;
  }
  const n = parseInt(s, 10);
  return !isNaN(n) && n >= 5;
}

export function nextEpKey(ep) {
  const s = String(ep);
  if (s.includes('x')) {
    const [t, e] = s.split('x');
    return t + 'x' + (parseInt(e, 10) + 1);
  }
  const n = parseInt(s, 10);
  if (isNaN(n)) return null;
  return String(n + 1);
}

export default function Player({ slug, ep, title, total }) {
  const videoRef = useRef(null);
  const wrapRef = useRef(null);
  const hlsRef = useRef(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [muted, setMuted] = useState(false);
  const [idle, setIdle] = useState(false);
  const [subtitles, setSubtitles] = useState([]);
  const [currentSubtitle, setCurrentSubtitle] = useState('');
  const [selectedSubLang, setSelectedSubLang] = useState('es');
  const [showSubMenu, setShowSubMenu] = useState(false);
  const [isAdLocked, setIsAdLocked] = useState(false);
  const [adClicksDone, setAdClicksDone] = useState(0);
  const [isVerifying, setIsVerifying] = useState(false);
  const [popupBlocked, setPopupBlocked] = useState(false);
  const cuesRef = useRef([]);
  const idleTimer = useRef(null);
  const router = useRouter();

  // Estados del sistema inteligente de reporte automático de errores
  const [errorReportData, setErrorReportData] = useState(null);
  const [showTechDetails, setShowTechDetails] = useState(false);
  const reportedErrorsRef = useRef(new Set());

  const dispatchAutoErrorReport = (errData = {}) => {
    const key = `${slug}_${ep}_${errData.error_type || ''}_${errData.http_status || ''}`;
    if (reportedErrorsRef.current.has(key)) return;
    reportedErrorsRef.current.add(key);

    const reportObj = {
      slug,
      ep,
      title,
      error_type: errData.error_type || 'PLAYBACK_FAILURE',
      http_status: errData.http_status || null,
      stream_url: errData.stream_url || '',
      error_message: errData.error_message || 'Fallo al reproducir video',
      details: errData.details || {}
    };

    setErrorReportData(reportObj);
    reportVideoError(reportObj);
  };

  // Cargar preferencia de subtítulos guardada
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const savedLang = localStorage.getItem('dramia_sub_lang');
      if (savedLang) {
        setSelectedSubLang(savedLang);
      }
    }
  }, []);

  // Control de bloqueo por anuncios a partir del episodio 5 en todos los títulos
  useEffect(() => {
    if (isEpisodeAdRestricted(ep)) {
      setIsAdLocked(true);
      setAdClicksDone(0);
      if (videoRef.current) {
        videoRef.current.pause();
      }
    } else {
      setIsAdLocked(false);
      setAdClicksDone(0);
    }
  }, [ep, slug]);

  // Auto-ocultar controles: aparecen al tocar, se ocultan a los 3s
  const resetIdle = () => {
    setIdle(false);
    clearTimeout(idleTimer.current);
    idleTimer.current = setTimeout(() => setIdle(true), 3000);
  };

  useEffect(() => {
    resetIdle();
    const evs = ['mousemove', 'touchstart', 'click', 'keydown'];
    evs.forEach(e => window.addEventListener(e, resetIdle, { passive: true }));
    return () => { clearTimeout(idleTimer.current); evs.forEach(e => window.removeEventListener(e, resetIdle)); };
  }, []);

  // Cerrar menú de subtítulos al hacer click fuera
  useEffect(() => {
    const handleOutsideClick = () => setShowSubMenu(false);
    if (showSubMenu) {
      document.addEventListener('click', handleOutsideClick);
    }
    return () => document.removeEventListener('click', handleOutsideClick);
  }, [showSubMenu]);

  // Estado de pantalla completa
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Detectar cambios de pantalla completa reales
  useEffect(() => {
    const handleFsChange = () => {
      const isFs = Boolean(
        document.fullscreenElement ||
        document.webkitFullscreenElement ||
        document.mozFullScreenElement ||
        document.msFullscreenElement
      );
      setIsFullscreen(isFs);
    };

    document.addEventListener('fullscreenchange', handleFsChange);
    document.addEventListener('webkitfullscreenchange', handleFsChange);
    document.addEventListener('mozfullscreenchange', handleFsChange);
    document.addEventListener('MSFullscreenChange', handleFsChange);

    return () => {
      document.removeEventListener('fullscreenchange', handleFsChange);
      document.removeEventListener('webkitfullscreenchange', handleFsChange);
      document.removeEventListener('mozfullscreenchange', handleFsChange);
      document.removeEventListener('MSFullscreenChange', handleFsChange);
    };
  }, []);

  const toggleFullscreen = () => {
    const wrap = wrapRef.current;
    const video = videoRef.current;
    if (!wrap) return;

    const isFs = Boolean(
      document.fullscreenElement ||
      document.webkitFullscreenElement ||
      document.mozFullScreenElement ||
      document.msFullscreenElement
    );

    if (!isFs) {
      if (wrap.requestFullscreen) {
        wrap.requestFullscreen().catch(() => {
          if (video?.requestFullscreen) video.requestFullscreen().catch(() => {});
          else if (video?.webkitEnterFullscreen) video.webkitEnterFullscreen();
        });
      } else if (wrap.webkitRequestFullscreen) {
        wrap.webkitRequestFullscreen();
      } else if (video?.webkitEnterFullscreen) {
        video.webkitEnterFullscreen();
      }
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen().catch(() => {});
      } else if (document.webkitExitFullscreen) {
        document.webkitExitFullscreen();
      }
    }
  };

  // Carga y parseo confiable de subtítulos dinámico según idioma seleccionado
  useEffect(() => {
    if (!subtitles || subtitles.length === 0 || selectedSubLang === 'off') {
      cuesRef.current = [];
      setCurrentSubtitle('');
      return;
    }
    let cancelled = false;

    async function loadCues() {
      // Buscar el subtítulo que coincide con selectedSubLang ('es', 'en', etc.)
      const matchSub = subtitles.find(s => s.lang === selectedSubLang) || 
                       subtitles.find(s => s.default) || 
                       subtitles[0];

      if (!matchSub || !matchSub.url) {
        cuesRef.current = [];
        setCurrentSubtitle('');
        return;
      }

      try {
        const res = await fetch(matchSub.url);
        if (!res.ok) return;
        const text = await res.text();
        if (cancelled) return;

        const lines = text.split('\n');
        const parseTime = (tStr) => {
          const p = tStr.trim().split(':');
          if (p.length === 3) return parseFloat(p[0]) * 3600 + parseFloat(p[1]) * 60 + parseFloat(p[2]);
          if (p.length === 2) return parseFloat(p[0]) * 60 + parseFloat(p[1]);
          return 0;
        };

        const parsed = [];
        let i = 0;
        while (i < lines.length) {
          const line = lines[i].trim();
          if (line.includes('-->')) {
            const [sStr, eStr] = line.split('-->');
            const start = parseTime(sStr);
            const end = parseTime(eStr);
            i++;
            let cueText = '';
            while (i < lines.length && lines[i].trim() !== '') {
              cueText += (cueText ? '\n' : '') + lines[i].trim();
              i++;
            }
            if (cueText && !isNaN(start) && !isNaN(end)) {
              parsed.push({ start, end, text: cueText });
            }
          }
          i++;
        }
        cuesRef.current = parsed;
      } catch (e) {
        cuesRef.current = [];
      }
    }

    loadCues();
    return () => { cancelled = true; };
  }, [subtitles, selectedSubLang]);

  const handleSelectLanguage = (lang) => {
    setSelectedSubLang(lang);
    if (typeof window !== 'undefined') {
      localStorage.setItem('dramia_sub_lang', lang);
    }
    setShowSubMenu(false);
  };

  // Actualización fluida del subtítulo activo según currentTime del video
  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    let animId;
    const checkTime = () => {
      const t = video.currentTime;
      const cues = cuesRef.current;
      if (cues && cues.length > 0) {
        const active = cues.filter(c => t >= c.start && t <= c.end);
        const txt = active.map(c => c.text).join('\n');
        setCurrentSubtitle(txt);
      } else {
        setCurrentSubtitle('');
      }
      if (!video.paused && !video.ended) {
        animId = requestAnimationFrame(checkTime);
      }
    };

    const handlePlay = () => {
      animId = requestAnimationFrame(checkTime);
    };
    const handlePause = () => {
      cancelAnimationFrame(animId);
      checkTime();
    };

    video.addEventListener('timeupdate', checkTime);
    video.addEventListener('play', handlePlay);
    video.addEventListener('pause', handlePause);
    video.addEventListener('seeked', checkTime);

    return () => {
      cancelAnimationFrame(animId);
      video.removeEventListener('timeupdate', checkTime);
      video.removeEventListener('play', handlePlay);
      video.removeEventListener('pause', handlePause);
      video.removeEventListener('seeked', checkTime);
    };
  }, []);

  const [reloadKey, setReloadKey] = useState(0);

  // Carga del episodio y video
  useEffect(() => {
    let cancelled = false;
    let autoRetryTimer = null;

    async function load(isFresh = false, retryCount = 0) {
      setLoading(true); setError('');
      fetch('/proxy/warmup?slug=' + encodeURIComponent(slug) + '&ep=' + encodeURIComponent(ep), { cache: 'no-store' }).catch(() => {});
      if (hlsRef.current) { try { hlsRef.current.destroy(); } catch (e) {} hlsRef.current = null; }
      const video = videoRef.current;
      if (!video) return;

      try {
        const epUrl = '/proxy/episode?slug=' + encodeURIComponent(slug) + '&ep=' + encodeURIComponent(ep) + (isFresh ? '&fresh=1' : '');
        const res = await fetch(epUrl, { cache: 'no-store' });
        if (!res.ok) {
          if (retryCount < 2) {
            autoRetryTimer = setTimeout(() => {
              if (!cancelled) load(true, retryCount + 1);
            }, 1200);
            return;
          }
          dispatchAutoErrorReport({
            error_type: 'HTTP_' + res.status,
            http_status: res.status,
            stream_url: epUrl,
            error_message: 'Fallo al consultar endpoint de episodio (' + res.status + ')'
          });
          throw new Error('Episodio no disponible (' + res.status + ')');
        }
        const data = await res.json();
        if (data.encrypted) throw new Error('ENCRYPTED');

        // Subtítulos
        if (data.subtitles && Array.isArray(data.subtitles) && data.subtitles.length > 0) {
          setSubtitles(data.subtitles);
        } else {
          setSubtitles([]);
        }

        let info;
        if (data.player_url) {
          let isHls = data.player_type === 'hls' || data.type === 'hls';
          if (data.player_url.includes('/proxy/stream')) isHls = false;
          if (data.player_url.includes('/proxy/manifest')) isHls = true;
          if (data.player_type === 'file' || data.type === 'mp4') isHls = false;
          info = { type: isHls ? 'hls' : 'file', url: data.player_url };
        } else {
          const first = (data.sources && data.sources[0]) || null;
          if (!first || !first.url) throw new Error('Episodio sin fuente de video');
          let url = first.url;
          if (url.startsWith('/')) url = 'https://esdramia.com' + url;
          const isHls = data.type === 'hls' || url.endsWith('s3hls');
          info = { type: isHls ? 'hls' : 'file', url: isHls ? '/proxy/manifest?url=' + encodeURIComponent(url) : '/proxy/stream?url=' + encodeURIComponent(url) };
        }
        if (cancelled) return;
        trackVideoPlay(slug, ep, data.title || title);
        video.muted = false;
        const tryPlay = () => {
          if (isEpisodeAdRestricted(ep) && isAdLocked) {
            return;
          }
          video.play().catch(() => { video.muted = true; setMuted(true); video.play().catch(() => {}); });
        };
        video.onerror = () => {
          if (!cancelled) {
            if (retryCount < 2) {
              autoRetryTimer = setTimeout(() => {
                if (!cancelled) load(true, retryCount + 1);
              }, 1200);
            } else {
              setLoading(false);
              const errCode = video.error?.code;
              const codeMap = { 1: 'MEDIA_ABORTED', 2: 'MEDIA_NETWORK', 3: 'MEDIA_DECODE', 4: 'SRC_NOT_SUPPORTED_OR_403' };
              dispatchAutoErrorReport({
                error_type: codeMap[errCode] || 'VIDEO_ELEMENT_ERROR',
                error_message: 'Fallo al reproducir video en el navegador (' + (codeMap[errCode] || ('código ' + errCode)) + ')',
                stream_url: info?.url || video.src || '',
                details: { code: errCode, message: video.error?.message }
              });
              setError('No se pudo reproducir el video en el navegador');
            }
          }
        };

        if (info.type === 'file') {
          video.src = info.url;
          video.addEventListener('loadedmetadata', () => { setLoading(false); tryPlay(); }, { once: true });
          video.addEventListener('canplay', () => { setLoading(false); }, { once: true });
        } else {
          const Hls = (await import('hls.js')).default;
          if (Hls.isSupported()) {
            const hls = new Hls({
              enableWorker: true,
              lowLatencyMode: false,
              capLevelToPlayerSize: true,
              maxBufferLength: 30,
              maxMaxBufferLength: 60,
              manifestLoadingMaxRetry: 5,
              manifestLoadingRetryDelay: 1000,
              levelLoadingMaxRetry: 5,
              fragLoadingMaxRetry: 6,
              fragLoadingRetryDelay: 800,
              fragLoadingMaxRetryTimeout: 10000,
            });
            hlsRef.current = hls;
            hls.loadSource(info.url);
            hls.attachMedia(video);
            hls.on(Hls.Events.MANIFEST_PARSED, () => {
              setLoading(false);
              tryPlay();
            });
            hls.on(Hls.Events.FRAG_BUFFERED, () => {
              setLoading(false);
            });
            let retryNetworkCount = 0;
            hls.on(Hls.Events.ERROR, (e, d) => {
              if (!d.fatal) {
                if (d.details === 'bufferStalledError') {
                  video.play().catch(() => {});
                }
                return;
              }
              if (d.type === 'mediaError') {
                hls.recoverMediaError();
                return;
              }
              if (d.type === 'networkError') {
                retryNetworkCount++;
                if (retryNetworkCount <= 3) {
                  setTimeout(() => {
                    if (!cancelled && hlsRef.current) hls.startLoad();
                  }, 1000);
                  return;
                }
                if (!isFresh) {
                  load(true);
                  return;
                }
                setLoading(false);
                dispatchAutoErrorReport({
                  error_type: 'HLS_NETWORK_ERROR',
                  http_status: d.response?.code || null,
                  stream_url: d.url || info?.url || '',
                  error_message: 'Fallo de red al descargar segmentos o manifiesto HLS',
                  details: { type: d.type, details: d.details, status: d.response?.code }
                });
                setError('Error de conexión al cargar segmentos de video');
                return;
              }
              if (d.details === 'manifestParsingError' || d.details === 'manifestLoadError') {
                if (info.url && info.url.includes('/proxy/manifest')) {
                  const fallbackUrl = info.url.replace('/proxy/manifest', '/proxy/stream');
                  try { hls.destroy(); } catch (_) {}
                  hlsRef.current = null;
                  video.src = fallbackUrl;
                  video.addEventListener('loadedmetadata', () => { setLoading(false); tryPlay(); }, { once: true });
                  video.addEventListener('canplay', () => { setLoading(false); }, { once: true });
                  return;
                }
              }
              setLoading(false);
              dispatchAutoErrorReport({
                error_type: 'HLS_' + (d.details || 'FORMAT_ERROR').toUpperCase(),
                http_status: d.response?.code || null,
                stream_url: d.url || info?.url || '',
                error_message: 'Fallo fatal de decodificación o formato HLS (' + d.details + ')',
                details: { type: d.type, details: d.details }
              });
              setError('Error al procesar el formato de video');
            });
          } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
            video.src = info.url;
            video.addEventListener('loadedmetadata', () => { setLoading(false); tryPlay(); }, { once: true });
          } else { setError('Navegador sin soporte HLS'); setLoading(false); }
        }
      } catch (e) {
        if (!cancelled) {
          if (!isFresh) {
            autoRetryTimer = setTimeout(() => {
              if (!cancelled) load(true);
            }, 1200);
          } else {
            dispatchAutoErrorReport({
              error_type: e.message === 'ENCRYPTED' ? 'ENCRYPTED_STREAM' : 'CLIENT_PLAYBACK_EXCEPTION',
              error_message: e.message,
              stream_url: '/proxy/episode?slug=' + encodeURIComponent(slug) + '&ep=' + encodeURIComponent(ep),
              details: { stack: e.stack }
            });
            setError(e.message === 'ENCRYPTED' ? '🔒 Contenido protegido' : e.message);
            setLoading(false);
          }
        }
      }
    }
    load(reloadKey > 0);
    return () => {
      cancelled = true;
      if (autoRetryTimer) clearTimeout(autoRetryTimer);
      if (hlsRef.current) { try { hlsRef.current.destroy(); } catch (e) {} hlsRef.current = null; }
    };
  }, [slug, ep, reloadKey]);

  const n = parseInt(ep, 10) || 1;

  // Prefetch del siguiente episodio en segundo plano para arranque instantáneo
  useEffect(() => {
    if (!loading && !error && n < total) {
      const nextEp = String(n + 1);
      fetch('/proxy/episode?slug=' + encodeURIComponent(slug) + '&ep=' + encodeURIComponent(nextEp)).catch(() => {});
    }
  }, [loading, error, n, total, slug]);

  // Telemetría en tiempo real: registra espectadores activos mientras el video se reproduce
  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    let heartbeatTimer = null;

    const pingWatching = () => {
      if (!video.paused && !video.ended && video.readyState >= 2) {
        trackLiveHeartbeat(true, slug, ep, title);
      }
    };

    const onPlayStart = () => {
      pingWatching();
      if (!heartbeatTimer) {
        heartbeatTimer = setInterval(pingWatching, 20000);
      }
    };

    const onPlayStop = () => {
      if (heartbeatTimer) {
        clearInterval(heartbeatTimer);
        heartbeatTimer = null;
      }
    };

    video.addEventListener('play', onPlayStart);
    video.addEventListener('playing', onPlayStart);
    video.addEventListener('pause', onPlayStop);
    video.addEventListener('ended', onPlayStop);

    return () => {
      if (heartbeatTimer) clearInterval(heartbeatTimer);
      video.removeEventListener('play', onPlayStart);
      video.removeEventListener('playing', onPlayStart);
      video.removeEventListener('pause', onPlayStop);
      video.removeEventListener('ended', onPlayStop);
    };
  }, [slug, ep, title]);

  const handleBack = (e) => {
    if (e) e.preventDefault();
    if (typeof window !== 'undefined') {
      const last = sessionStorage.getItem('dramia_last_section') || '/';
      try {
        const urlObj = new URL(last, window.location.origin);
        urlObj.searchParams.set('open', slug);
        router.push(urlObj.pathname + urlObj.search, { scroll: false });
      } catch (err) {
        router.push('/?open=' + encodeURIComponent(slug), { scroll: false });
      }
    }
  };

  const handleOpenAd = () => {
    if (isVerifying) return;

    const nextCount = adClicksDone + 1;
    const unlockUrl = `/api/unlock?step=${nextCount}&slug=${encodeURIComponent(slug || '')}&ep=${encodeURIComponent(ep || '1')}`;
    const adNetwork = (nextCount % 2 === 0) ? 'monetag' : 'adsterra';
    trackAdClick(slug, ep, adNetwork);

    setPopupBlocked(false);
    try {
      const win = window.open(unlockUrl, '_blank', 'noopener,noreferrer');
      if (!win || win.closed || typeof win.closed === 'undefined') {
        setPopupBlocked(true);
      }
    } catch (e) {
      setPopupBlocked(true);
    }

    setIsVerifying(true);
    setTimeout(() => {
      setIsVerifying(false);
      if (nextCount >= REQUIRED_AD_CLICKS) {
        setIsAdLocked(false);
        setAdClicksDone(nextCount);
        setTimeout(() => {
          if (videoRef.current) {
            videoRef.current.play().catch(() => {});
          }
        }, 300);
      } else {
        setAdClicksDone(nextCount);
      }
    }, 1400);
  };

  const handleDisagree = () => {
    handleBack();
  };

  const go = (d) => {
    let target;
    if (String(ep).includes('x')) {
      const [t, e] = String(ep).split('x');
      const ei = parseInt(e, 10) + d;
      if (ei < 1) return;
      target = t + 'x' + ei;
    } else {
      const t = n + d;
      if (t < 1 || t > total) return;
      target = String(t);
    }
    setLoading(true);
    setError('');
    router.push('/ver/' + slug + '/' + target, { scroll: false });
  };


  return (
    <div ref={wrapRef} className={'player-wrap' + (idle ? ' idle' : '')}>
      <div className="player-top">
        <button onClick={handleBack} className="player-back" aria-label="Volver" style={{ cursor: 'pointer', background: 'rgba(255,255,255,0.1)', border: 'none', borderRadius: '50%', width: 42, height: 42, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', transition: 'all 0.2s ease' }}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round" width="22" height="22">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
        </button>
        <div className="player-info">
          <h3>{title}</h3>
          <p>Episodio {ep} de {total}</p>
        </div>
        <div className="ep-nav">
          {subtitles && subtitles.length > 0 && (
            <div className="sub-selector-container">
              <button
                onClick={(e) => { e.stopPropagation(); setShowSubMenu(!showSubMenu); }}
                className={'sub-btn' + (selectedSubLang !== 'off' ? ' active' : '')}
                title="Subtítulos"
                aria-label="Seleccionar idioma de subtítulos"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" width="16" height="16">
                  <rect x="2" y="4" width="20" height="16" rx="3" />
                  <path d="M7 15h3M7 11h3M14 15h3M14 11h3" />
                </svg>
                <span className="lbl">{selectedSubLang === 'off' ? 'CC: Off' : selectedSubLang.toUpperCase()}</span>
              </button>

              {showSubMenu && (
                <div className="sub-menu-dropdown" onClick={(e) => e.stopPropagation()}>
                  <div className="sub-menu-title">Idioma de Subtítulos</div>
                  {subtitles.some(s => s.lang === 'es') && (
                    <button
                      className={'sub-menu-option' + (selectedSubLang === 'es' ? ' selected' : '')}
                      onClick={() => handleSelectLanguage('es')}
                    >
                      <span className="sub-opt-name">🇪🇸 Español</span>
                      {selectedSubLang === 'es' && <span className="sub-opt-check">✓</span>}
                    </button>
                  )}
                  {subtitles.some(s => s.lang === 'en' || s.lang === 'en-US') && (
                    <button
                      className={'sub-menu-option' + (selectedSubLang === 'en' ? ' selected' : '')}
                      onClick={() => handleSelectLanguage('en')}
                    >
                      <span className="sub-opt-name">🇬🇧 English</span>
                      {selectedSubLang === 'en' && <span className="sub-opt-check">✓</span>}
                    </button>
                  )}
                  <button
                    className={'sub-menu-option' + (selectedSubLang === 'off' ? ' selected' : '')}
                    onClick={() => handleSelectLanguage('off')}
                  >
                    <span className="sub-opt-name">🚫 Desactivados</span>
                    {selectedSubLang === 'off' && <span className="sub-opt-check">✓</span>}
                  </button>
                </div>
              )}
            </div>
          )}
          <button onClick={() => go(-1)} disabled={n <= 1} title="Episodio anterior" aria-label="Episodio anterior">
            <span className="ep-arrow">◀</span>
            <span className="lbl">Anterior</span>
          </button>
          <button onClick={() => go(1)} disabled={n >= total} title="Episodio siguiente" aria-label="Episodio siguiente">
            <span className="lbl">Siguiente</span>
            <span className="ep-arrow">▶</span>
          </button>
          <button onClick={toggleFullscreen} className="fs-btn" title={isFullscreen ? 'Salir de pantalla completa' : 'Pantalla completa'} aria-label="Pantalla completa">
            {isFullscreen ? (
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" width="17" height="17">
                <path d="M8 3v3a2 2 0 0 1-2 2H3m18 0h-3a2 2 0 0 1-2-2V3m0 18v-3a2 2 0 0 1 2-2h3M3 16h3a2 2 0 0 1 2 2v3"/>
              </svg>
            ) : (
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" width="17" height="17">
                <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/>
              </svg>
            )}
            <span className="lbl">{isFullscreen ? 'Normal' : 'Expandir'}</span>
          </button>
        </div>
      </div>
      <div className="player-stage">
        {loading && <div className="player-loading"><div className="spinner" /><span>Cargando…</span></div>}
        {error && (
          <div className="player-error" style={{
            background: 'linear-gradient(180deg, rgba(17, 17, 24, 0.98), rgba(10, 10, 15, 0.98))',
            border: '1px solid rgba(239, 68, 68, 0.35)',
            boxShadow: '0 20px 50px rgba(0, 0, 0, 0.8), 0 0 30px rgba(229, 9, 20, 0.15)',
            borderRadius: '16px',
            padding: '24px 20px',
            maxWidth: '420px',
            margin: '0 auto',
            backdropFilter: 'blur(12px)',
            zIndex: 30
          }}>
            <div style={{
              width: 52,
              height: 52,
              margin: '0 auto 12px',
              borderRadius: '50%',
              background: 'rgba(239, 68, 68, 0.15)',
              border: '1px solid rgba(239, 68, 68, 0.4)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '24px'
            }}>
              ⚠️
            </div>

            <h3 style={{ fontSize: '17px', fontWeight: '800', color: '#fff', margin: '0 0 6px' }}>
              No se pudo cargar el video
            </h3>
            
            <p style={{ margin: '0 0 14px', fontSize: '13px', color: '#cbd5e1', lineHeight: 1.4 }}>
              {error}
            </p>

            {/* Banner de reporte automático e inteligente */}
            <div style={{
              background: 'rgba(34, 197, 94, 0.1)',
              border: '1px solid rgba(34, 197, 94, 0.3)',
              borderRadius: '10px',
              padding: '10px 12px',
              marginBottom: '16px',
              textAlign: 'left',
              display: 'flex',
              alignItems: 'flex-start',
              gap: '10px'
            }}>
              <span style={{ fontSize: '16px', marginTop: '1px' }}>🛡️</span>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: '12px', fontWeight: '800', color: '#4ade80', marginBottom: '2px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span>Reporte enviado automáticamente</span>
                  <span style={{ fontSize: '10px', background: '#22c55e', color: '#000', padding: '1px 5px', borderRadius: '4px', fontWeight: '900' }}>OK</span>
                </div>
                <div style={{ fontSize: '11px', color: '#a1a1aa', lineHeight: 1.35 }}>
                  El sistema capturó los logs técnicos y notificó al panel de soporte. No es necesario que envíes nada manualmente.
                </div>
              </div>
            </div>

            {errorReportData && (
              <div style={{ marginBottom: '14px', textAlign: 'left' }}>
                <button
                  type="button"
                  onClick={() => setShowTechDetails(!showTechDetails)}
                  style={{
                    background: 'transparent',
                    border: 'none',
                    color: '#71717a',
                    fontSize: '11px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                    padding: 0
                  }}
                >
                  <span>{showTechDetails ? '▼ Ocultar detalles técnicos' : '▶ Ver detalles técnicos'}</span>
                </button>
                {showTechDetails && (
                  <pre style={{
                    margin: '8px 0 0',
                    background: '#07070a',
                    border: '1px solid rgba(255,255,255,0.08)',
                    borderRadius: '8px',
                    padding: '8px',
                    fontSize: '10px',
                    color: '#e2e8f0',
                    maxHeight: '110px',
                    overflowX: 'auto',
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-all'
                  }}>
                    {JSON.stringify({
                      tipo: errorReportData.error_type,
                      status: errorReportData.http_status,
                      url: errorReportData.stream_url ? errorReportData.stream_url.slice(0, 90) + '...' : null
                    }, null, 2)}
                  </pre>
                )}
              </div>
            )}

            <div style={{ display: 'flex', gap: '8px', justifyContent: 'center' }}>
              <button
                onClick={() => { setError(''); setLoading(true); setReloadKey(k => k + 1); }}
                className="player-retry-btn"
                style={{ flex: 1 }}
              >
                🔄 Reintentar conexión
              </button>
              <button
                onClick={handleBack}
                style={{
                  background: 'rgba(255, 255, 255, 0.08)',
                  border: '1px solid rgba(255, 255, 255, 0.15)',
                  color: '#e4e4e7',
                  borderRadius: '8px',
                  padding: '9px 14px',
                  fontSize: '12px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
              >
                Volver
              </button>
            </div>
          </div>
        )}
        <video
          ref={videoRef}
          controls
          controlsList="nodownload"
          playsInline
          autoPlay={!isAdLocked}
          muted={muted}
          crossOrigin="anonymous"
          onContextMenu={(e) => e.preventDefault()}
        />
        {currentSubtitle && (
          <div className="custom-subtitle-box">
            <span className="custom-subtitle-text">{currentSubtitle}</span>
          </div>
        )}

        {/* Modal Emergente de Anuncios Adsterra & Monetag Cloaked */}
        {isAdLocked && (
          <div className="ad-modal-backdrop">
            <div className="ad-modal-card" onClick={(e) => e.stopPropagation()}>
              <div className="ad-modal-banner">
                <div className="ad-modal-banner-glow" />
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="48" height="48">
                  <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
                  <line x1="8" y1="21" x2="16" y2="21"/>
                  <line x1="12" y1="17" x2="12" y2="21"/>
                </svg>
              </div>
              <h2 className="ad-modal-title">Publicidad para continuar</h2>
              <p className="ad-modal-subtitle">
                Faltan {REQUIRED_AD_CLICKS - adClicksDone} de {REQUIRED_AD_CLICKS} anuncios para desbloquear
              </p>

              {popupBlocked && (
                <div style={{
                  background: 'rgba(239, 68, 68, 0.18)',
                  border: '1px solid rgba(239, 68, 68, 0.4)',
                  borderRadius: 10,
                  padding: '8px 12px',
                  fontSize: 12,
                  color: '#fca5a5',
                  margin: '10px 0',
                  lineHeight: 1.35,
                  textAlign: 'center'
                }}>
                  ⚠️ Pestaña bloqueada por el navegador. Permite las ventanas emergentes para completar el desbloqueo.
                </div>
              )}
              
              <div className="ad-progress-dots" style={{ marginTop: 14 }}>
                {Array.from({ length: REQUIRED_AD_CLICKS }).map((_, idx) => (
                  <div
                    key={idx}
                    className={'ad-dot' + (idx < adClicksDone ? ' active' : idx === adClicksDone ? ' current' : '')}
                  />
                ))}
              </div>

              <div className="ad-modal-actions">
                <button
                  onClick={handleOpenAd}
                  className="ad-btn-open"
                  disabled={isVerifying}
                  style={isVerifying ? { opacity: 0.75, cursor: 'wait' } : {}}
                  aria-label="Abrir patrocinador"
                >
                  {isVerifying ? (
                    <>
                      <div className="spinner" style={{ width: 14, height: 14, borderWidth: 2, marginRight: 4, display: 'inline-block' }} />
                      Verificando ({adClicksDone + 1}/{REQUIRED_AD_CLICKS})...
                    </>
                  ) : (
                    <>
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" width="16" height="16">
                        <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6M15 3h6v6M10 14L21 3" />
                      </svg>
                      Abrir anuncio ({adClicksDone + 1}/{REQUIRED_AD_CLICKS})
                    </>
                  )}
                </button>
                <button onClick={handleDisagree} className="ad-btn-disagree" aria-label="Volver">
                  Volver
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
