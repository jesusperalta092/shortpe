'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { authenticateAdmin, fetchAdminDashboard } from '../../lib/analytics';

export default function AdminDashboardPage() {
  const [sessionToken, setSessionToken] = useState(null);
  const [pinInput, setPinInput] = useState('');
  const [authError, setAuthError] = useState('');
  const [authLoading, setAuthLoading] = useState(false);

  const [timeRange, setTimeRange] = useState(7);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [serverStatus, setServerStatus] = useState('checking'); // 'live' | 'dead' | 'checking'

  // Cargar token previo de sessionStorage
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const saved = sessionStorage.getItem('dramape_admin_token');
      if (saved) {
        setSessionToken(saved);
      }
    }
  }, []);

  // Cargar datos y verificar estado del servidor cada 8 segundos
  useEffect(() => {
    if (!sessionToken) return;

    let isMounted = true;
    const loadMetrics = async () => {
      setLoading(true);
      try {
        const res = await fetchAdminDashboard(timeRange, sessionToken);
        if (!isMounted) return;

        if (res.unauthorized) {
          sessionStorage.removeItem('dramape_admin_token');
          setSessionToken(null);
          setAuthError('Sesión expirada. Ingresa tu PIN.');
          setServerStatus('dead');
        } else if (res.ok) {
          setData(res);
          setServerStatus('live');
          setLastUpdated(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }));
        } else {
          setServerStatus('dead');
        }
      } catch (e) {
        if (isMounted) setServerStatus('dead');
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    loadMetrics();
    const interval = setInterval(loadMetrics, 8000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, [sessionToken, timeRange]);

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!pinInput.trim()) return;
    setAuthLoading(true);
    setAuthError('');

    const res = await authenticateAdmin(pinInput);
    setAuthLoading(false);

    if (res.ok && res.token) {
      sessionStorage.setItem('dramape_admin_token', res.token);
      setSessionToken(res.token);
      setPinInput('');
    } else {
      setAuthError(res.error || 'PIN de acceso incorrecto');
    }
  };

  const handleLogout = () => {
    sessionStorage.removeItem('dramape_admin_token');
    setSessionToken(null);
    setData(null);
  };

  // ==========================================
  // 🔒 MODAL DE ACCESO COMPACTO Y ELEGANTE
  // ==========================================
  if (!sessionToken) {
    return (
      <div style={{
        minHeight: '100vh',
        backgroundColor: '#07070a',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '16px',
        fontFamily: 'system-ui, -apple-system, sans-serif'
      }}>
        <div style={{
          width: '100%',
          maxWidth: '350px',
          background: '#0f0f14',
          borderRadius: '16px',
          padding: '24px 22px',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          boxShadow: '0 20px 40px rgba(0, 0, 0, 0.8), 0 0 30px rgba(229, 9, 20, 0.1)',
          textAlign: 'center'
        }}>
          <div style={{
            width: '44px',
            height: '44px',
            margin: '0 auto 14px',
            borderRadius: '12px',
            background: 'linear-gradient(135deg, #e50914, #8b0000)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '20px',
            boxShadow: '0 4px 14px rgba(229, 9, 20, 0.35)'
          }}>
            🛡️
          </div>

          <h1 style={{ fontSize: '18px', fontWeight: '800', color: '#fff', margin: '0 0 4px', letterSpacing: '-0.01em' }}>
            Panel Drama<span style={{ color: '#e50914' }}>Pe</span>
          </h1>
          <p style={{ color: '#71717a', fontSize: '12px', margin: '0 0 20px' }}>
            Telemetría y analíticas en tiempo real
          </p>

          <form onSubmit={handleLogin}>
            <div style={{ marginBottom: '14px', textAlign: 'left' }}>
              <label style={{ display: 'block', color: '#a1a1aa', fontSize: '11px', fontWeight: '600', marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                PIN Maestro
              </label>
              <input
                type="password"
                placeholder="••••••"
                value={pinInput}
                onChange={(e) => setPinInput(e.target.value)}
                style={{
                  width: '100%',
                  padding: '10px 14px',
                  borderRadius: '8px',
                  background: 'rgba(255, 255, 255, 0.04)',
                  border: '1px solid rgba(255, 255, 255, 0.12)',
                  color: '#fff',
                  fontSize: '15px',
                  outline: 'none',
                  boxSizing: 'border-box',
                  textAlign: 'center',
                  letterSpacing: '0.25em'
                }}
                autoFocus
              />
            </div>

            {authError && (
              <div style={{
                background: 'rgba(229, 9, 20, 0.12)',
                border: '1px solid rgba(229, 9, 20, 0.3)',
                color: '#f87171',
                padding: '8px 10px',
                borderRadius: '6px',
                fontSize: '11.5px',
                marginBottom: '14px',
                textAlign: 'left'
              }}>
                ⚠️ {authError}
              </div>
            )}

            <button
              type="submit"
              disabled={authLoading}
              style={{
                width: '100%',
                padding: '10px',
                borderRadius: '8px',
                background: authLoading ? '#444' : '#e50914',
                color: '#fff',
                fontWeight: '700',
                fontSize: '13px',
                border: 'none',
                cursor: authLoading ? 'not-allowed' : 'pointer',
                boxShadow: '0 4px 12px rgba(229, 9, 20, 0.3)',
                transition: 'opacity 0.2s'
              }}
            >
              {authLoading ? 'Verificando...' : 'Desbloquear'}
            </button>
          </form>

          <div style={{ marginTop: '18px' }}>
            <Link href="/" style={{ color: '#52525b', fontSize: '12px', textDecoration: 'none' }}>
              ← Volver a DramaPe
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // ==========================================
  // 📊 DASHBOARD REFINADO CON CONTENEDORES AISLADOS
  // ==========================================
  const realtime = data?.realtime || { online_now: 0, watching_now: 0, active_streams: [] };
  const overview = data?.overview || {};
  const timeline = data?.timeline || [];
  const topDramas = data?.top_dramas || [];
  const devices = data?.devices || { mobile: 0, desktop: 0, tablet: 0 };
  const totalDevices = (devices.mobile || 0) + (devices.desktop || 0) + (devices.tablet || 0) || 1;

  const maxTimelineViews = Math.max(...timeline.map(t => Math.max(t.views || 0, t.visitors || 0, t.plays || 0)), 1);

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#08080c',
      color: '#f4f4f5',
      fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      padding: '24px 20px 48px',
      boxSizing: 'border-box'
    }}>
      <div style={{ maxWidth: '1140px', margin: '0 auto' }}>
        
        {/* HEADER CONTENEDOR RELATIVO (NO USA ETIQUETA HEADER PARA EVITAR CONFLICTO CON GLOBALS.CSS) */}
        <div style={{
          position: 'relative',
          width: '100%',
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '14px',
          padding: '14px 20px',
          background: 'rgba(18, 18, 24, 0.95)',
          borderRadius: '12px',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          boxShadow: '0 8px 24px rgba(0, 0, 0, 0.5)',
          marginBottom: '24px'
        }}>
          {/* LOGO + ESTADO DEL SERVIDOR */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{
              background: '#e50914',
              color: '#fff',
              fontSize: '11px',
              fontWeight: '900',
              padding: '3px 8px',
              borderRadius: '5px',
              letterSpacing: '0.04em'
            }}>PRO</div>
            
            <div style={{ fontSize: '16px', fontWeight: '800', letterSpacing: '-0.02em', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span>DramaPe</span>
              <span style={{ color: '#71717a', fontSize: '13px', fontWeight: '500' }}>/ Analíticas</span>
            </div>

            {/* BADGE DE ESTADO DEL SERVIDOR: LIVE / DEAD */}
            <div style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              padding: '4px 10px',
              borderRadius: '20px',
              fontSize: '11px',
              fontWeight: '800',
              marginLeft: '6px',
              background: serverStatus === 'live' 
                ? 'rgba(34, 197, 94, 0.15)' 
                : serverStatus === 'dead' 
                ? 'rgba(239, 68, 68, 0.2)' 
                : 'rgba(255, 255, 255, 0.08)',
              border: `1px solid ${
                serverStatus === 'live' 
                  ? 'rgba(34, 197, 94, 0.35)' 
                  : serverStatus === 'dead' 
                  ? 'rgba(239, 68, 68, 0.5)' 
                  : 'rgba(255, 255, 255, 0.12)'
              }`,
              color: serverStatus === 'live' ? '#4ade80' : serverStatus === 'dead' ? '#f87171' : '#a1a1aa'
            }}>
              <span style={{
                width: '7px',
                height: '7px',
                borderRadius: '50%',
                backgroundColor: serverStatus === 'live' ? '#4ade80' : serverStatus === 'dead' ? '#ef4444' : '#a1a1aa',
                boxShadow: serverStatus === 'live' ? '0 0 8px #4ade80' : serverStatus === 'dead' ? '0 0 8px #ef4444' : 'none'
              }}></span>
              {serverStatus === 'live' ? 'LIVE' : serverStatus === 'dead' ? 'DEAD' : 'CHECKING...'}
            </div>
          </div>

          {/* CONTROLES DEL HEADER */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
            {/* SELECTOR DE DÍAS */}
            <div style={{
              display: 'inline-flex',
              background: 'rgba(255, 255, 255, 0.04)',
              borderRadius: '7px',
              padding: '2px',
              border: '1px solid rgba(255, 255, 255, 0.08)'
            }}>
              {[
                { label: 'Hoy', value: 1 },
                { label: '7D', value: 7 },
                { label: '30D', value: 30 },
                { label: '90D', value: 90 }
              ].map(opt => (
                <button
                  key={opt.value}
                  onClick={() => setTimeRange(opt.value)}
                  style={{
                    padding: '4px 10px',
                    borderRadius: '5px',
                    fontSize: '11.5px',
                    fontWeight: timeRange === opt.value ? '700' : '500',
                    background: timeRange === opt.value ? '#e50914' : 'transparent',
                    color: timeRange === opt.value ? '#fff' : '#a1a1aa',
                    border: 'none',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease'
                  }}
                >
                  {opt.label}
                </button>
              ))}
            </div>

            {/* BOTÓN SALIR */}
            <button
              onClick={handleLogout}
              style={{
                padding: '5px 12px',
                borderRadius: '7px',
                background: 'rgba(255, 255, 255, 0.06)',
                color: '#a1a1aa',
                border: '1px solid rgba(255, 255, 255, 0.08)',
                fontSize: '12px',
                cursor: 'pointer',
                fontWeight: '600'
              }}
            >
              Cerrar Sesión
            </button>
          </div>
        </div>

        {/* 📊 4 TARJETAS PRINCIPALES REFINADAS Y COMPACTAS */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(230px, 1fr))',
          gap: '14px',
          marginBottom: '20px'
        }}>
          {/* CARD 1: REPRODUCCIÓN EN VIVO */}
          <div style={{
            background: 'linear-gradient(135deg, rgba(229, 9, 20, 0.12), rgba(18, 18, 24, 0.9))',
            borderRadius: '12px',
            padding: '16px 18px',
            border: '1px solid rgba(229, 9, 20, 0.3)',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span style={{ color: '#f87171', fontSize: '11px', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Mirando Video Ahora
              </span>
              <span style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '4px',
                background: 'rgba(229, 9, 20, 0.25)',
                color: '#ef4444',
                padding: '2px 7px',
                borderRadius: '10px',
                fontSize: '10px',
                fontWeight: '800'
              }}>
                <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: '#ef4444' }}></span>
                EN VIVO
              </span>
            </div>
            <div style={{ fontSize: '26px', fontWeight: '800', color: '#fff', lineHeight: 1 }}>
              {realtime.watching_now}
            </div>
            <div style={{ color: '#fca5a5', fontSize: '11.5px', marginTop: '6px' }}>
              {realtime.watching_now === 1 ? '1 persona reproduciendo video' : `${realtime.watching_now} personas reproduciendo`}
            </div>
          </div>

          {/* CARD 2: VISITANTES EN LÍNEA */}
          <div style={{
            background: 'linear-gradient(135deg, rgba(34, 197, 94, 0.1), rgba(18, 18, 24, 0.9))',
            borderRadius: '12px',
            padding: '16px 18px',
            border: '1px solid rgba(34, 197, 94, 0.25)',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span style={{ color: '#86efac', fontSize: '11px', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Navegando Online
              </span>
              <span style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '4px',
                background: 'rgba(34, 197, 94, 0.2)',
                color: '#4ade80',
                padding: '2px 7px',
                borderRadius: '10px',
                fontSize: '10px',
                fontWeight: '800'
              }}>
                <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: '#4ade80' }}></span>
                ACTIVO
              </span>
            </div>
            <div style={{ fontSize: '26px', fontWeight: '800', color: '#fff', lineHeight: 1 }}>
              {realtime.online_now}
            </div>
            <div style={{ color: '#bbf7d0', fontSize: '11.5px', marginTop: '6px' }}>
              Usuarios explorando la plataforma
            </div>
          </div>

          {/* CARD 3: VISITAS HOY */}
          <div style={{
            background: 'rgba(18, 18, 24, 0.9)',
            borderRadius: '12px',
            padding: '16px 18px',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between'
          }}>
            <div style={{ color: '#a1a1aa', fontSize: '11px', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '8px' }}>
              Visitas Únicas Hoy
            </div>
            <div style={{ fontSize: '26px', fontWeight: '800', color: '#fff', lineHeight: 1 }}>
              {overview.today_visitors || 0}
            </div>
            <div style={{ color: '#71717a', fontSize: '11.5px', marginTop: '6px' }}>
              {overview.today_plays || 0} reproducciones hoy
            </div>
          </div>

          {/* CARD 4: PLAYS TOTALES */}
          <div style={{
            background: 'rgba(18, 18, 24, 0.9)',
            borderRadius: '12px',
            padding: '16px 18px',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between'
          }}>
            <div style={{ color: '#a1a1aa', fontSize: '11px', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '8px' }}>
              Total Plays ({timeRange}D)
            </div>
            <div style={{ fontSize: '26px', fontWeight: '800', color: '#fff', lineHeight: 1 }}>
              {overview.video_plays || 0}
            </div>
            <div style={{ color: '#71717a', fontSize: '11.5px', marginTop: '6px' }}>
              {overview.unique_visitors || 0} visitantes únicos en el periodo
            </div>
          </div>
        </div>

        {/* 👁️ TRANSMISIONES EN VIVO (COMPACTO) */}
        <div style={{
          background: 'rgba(18, 18, 24, 0.9)',
          borderRadius: '12px',
          padding: '16px 18px',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          marginBottom: '20px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <h2 style={{ fontSize: '14px', fontWeight: '700', margin: 0, display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span>👁️</span> Reproducciones en Tiempo Real
            </h2>
            <span style={{ fontSize: '11px', color: '#71717a' }}>
              Refresco: {lastUpdated || 'Cargando...'}
            </span>
          </div>

          {realtime.active_streams && realtime.active_streams.length > 0 ? (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '8px' }}>
              {realtime.active_streams.map((stream, idx) => (
                <div
                  key={idx}
                  style={{
                    background: 'rgba(255, 255, 255, 0.02)',
                    border: '1px solid rgba(229, 9, 20, 0.2)',
                    borderRadius: '8px',
                    padding: '8px 12px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between'
                  }}
                >
                  <div style={{ overflow: 'hidden', paddingRight: '8px' }}>
                    <div style={{ fontWeight: '600', color: '#fff', fontSize: '12.5px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {stream.title}
                    </div>
                    <div style={{ fontSize: '11px', color: '#71717a', marginTop: '1px', display: 'flex', gap: '6px' }}>
                      <span style={{ color: '#ef4444', fontWeight: '700' }}>Ep. {stream.ep || '1'}</span>
                      <span>•</span>
                      <span>{stream.device === 'mobile' ? '📱 Móvil' : stream.device === 'tablet' ? '📟 Tablet' : '💻 PC'}</span>
                    </div>
                  </div>
                  <div style={{
                    fontSize: '10px',
                    color: '#4ade80',
                    background: 'rgba(34, 197, 94, 0.12)',
                    padding: '3px 6px',
                    borderRadius: '4px',
                    whiteSpace: 'nowrap',
                    fontWeight: '600'
                  }}>
                    hace {stream.seconds_ago}s
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '16px 0', color: '#71717a', fontSize: '12.5px' }}>
              No hay usuarios reproduciendo video en este segundo exacto. Los visitantes están navegando el catálogo.
            </div>
          )}
        </div>

        {/* 📈 GRÁFICO DIARIO + TOP DORAMAS (GRID 2 COLUMNAS) */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))',
          gap: '16px',
          marginBottom: '20px'
        }}>
          {/* LÍNEA DE TIEMPO */}
          <div style={{
            background: 'rgba(18, 18, 24, 0.9)',
            borderRadius: '12px',
            padding: '16px 18px',
            border: '1px solid rgba(255, 255, 255, 0.08)'
          }}>
            <h2 style={{ fontSize: '14px', fontWeight: '700', margin: '0 0 14px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span>📈</span> Tendencia Diaria (Visitas / Plays)
            </h2>

            {timeline.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {timeline.slice(-7).map((day, idx) => {
                  const viewPct = Math.round(((day.views || 0) / maxTimelineViews) * 100);
                  const playPct = Math.round(((day.plays || 0) / maxTimelineViews) * 100);
                  return (
                    <div key={idx}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: '#a1a1aa', marginBottom: '3px' }}>
                        <span style={{ fontWeight: '600', color: '#e4e4e7' }}>{day.date_str}</span>
                        <span>
                          <strong style={{ color: '#fff' }}>{day.visitors || 0}</strong> visitas • <strong style={{ color: '#ef4444' }}>{day.plays || 0}</strong> plays
                        </span>
                      </div>
                      <div style={{ width: '100%', height: '5px', background: 'rgba(255, 255, 255, 0.04)', borderRadius: '3px', overflow: 'hidden', display: 'flex', gap: '2px' }}>
                        <div style={{ width: `${Math.min(viewPct, 100)}%`, background: '#3b82f6', borderRadius: '3px' }}></div>
                        <div style={{ width: `${Math.min(playPct, 100)}%`, background: '#ef4444', borderRadius: '3px' }}></div>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: '24px 0', color: '#71717a', fontSize: '12px' }}>
                Esperando registro de tráfico histórico...
              </div>
            )}
          </div>

          {/* TOP DORAMAS */}
          <div style={{
            background: 'rgba(18, 18, 24, 0.9)',
            borderRadius: '12px',
            padding: '16px 18px',
            border: '1px solid rgba(255, 255, 255, 0.08)'
          }}>
            <h2 style={{ fontSize: '14px', fontWeight: '700', margin: '0 0 14px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span>🏆</span> Top Doramas Más Vistos
            </h2>

            {topDramas.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {topDramas.slice(0, 7).map((drama, idx) => (
                  <div
                    key={drama.slug}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '6px 10px',
                      background: idx === 0 ? 'rgba(229, 9, 20, 0.08)' : 'rgba(255, 255, 255, 0.015)',
                      borderRadius: '6px',
                      border: idx === 0 ? '1px solid rgba(229, 9, 20, 0.25)' : '1px solid rgba(255, 255, 255, 0.03)'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', overflow: 'hidden' }}>
                      <span style={{
                        width: '18px',
                        height: '18px',
                        borderRadius: '4px',
                        background: idx === 0 ? '#e50914' : 'rgba(255, 255, 255, 0.08)',
                        color: '#fff',
                        fontSize: '10px',
                        fontWeight: '800',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        flexShrink: 0
                      }}>
                        {idx + 1}
                      </span>
                      <span style={{ fontSize: '12px', fontWeight: '500', color: '#e4e4e7', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {drama.display_title}
                      </span>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexShrink: 0 }}>
                      <span style={{ fontSize: '11px', fontWeight: '700', color: '#f87171' }}>
                        {drama.play_count} plays
                      </span>
                      <Link
                        href={`/ver/${encodeURIComponent(drama.slug)}/1`}
                        target="_blank"
                        style={{
                          background: 'rgba(255, 255, 255, 0.06)',
                          color: '#fff',
                          fontSize: '10px',
                          padding: '2px 6px',
                          borderRadius: '4px',
                          textDecoration: 'none',
                          fontWeight: '600'
                        }}
                      >
                        Ver ▶
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: '24px 0', color: '#71717a', fontSize: '12px' }}>
                Sin reproducciones registradas en este periodo.
              </div>
            )}
          </div>
        </div>

        {/* 📱 DISPOSITIVOS Y MONETIZACIÓN (COMPACTO) */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
          gap: '16px'
        }}>
          {/* DISPOSITIVOS */}
          <div style={{
            background: 'rgba(18, 18, 24, 0.9)',
            borderRadius: '12px',
            padding: '16px 18px',
            border: '1px solid rgba(255, 255, 255, 0.08)'
          }}>
            <h2 style={{ fontSize: '13px', fontWeight: '700', margin: '0 0 12px' }}>
              📱 Dispositivos
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {[
                { name: 'Móvil', count: devices.mobile || 0, icon: '📱', color: '#e50914' },
                { name: 'Desktop / PC', count: devices.desktop || 0, icon: '💻', color: '#3b82f6' },
                { name: 'Tablet', count: devices.tablet || 0, icon: '📟', color: '#10b981' }
              ].map(dev => {
                const pct = Math.round((dev.count / totalDevices) * 100);
                return (
                  <div key={dev.name}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11.5px', marginBottom: '3px' }}>
                      <span style={{ color: '#d4d4d8' }}>{dev.icon} {dev.name}</span>
                      <span style={{ fontWeight: '700', color: '#fff' }}>{pct}% ({dev.count})</span>
                    </div>
                    <div style={{ width: '100%', height: '4px', background: 'rgba(255, 255, 255, 0.04)', borderRadius: '2px', overflow: 'hidden' }}>
                      <div style={{ width: `${pct}%`, height: '100%', background: dev.color, borderRadius: '2px' }}></div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* TELEMETRÍA DE ANUNCIOS */}
          <div style={{
            background: 'rgba(18, 18, 24, 0.9)',
            borderRadius: '12px',
            padding: '16px 18px',
            border: '1px solid rgba(255, 255, 255, 0.08)'
          }}>
            <h2 style={{ fontSize: '13px', fontWeight: '700', margin: '0 0 12px' }}>
              💰 Telemetría de Anuncios
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 10px', background: 'rgba(255, 255, 255, 0.02)', borderRadius: '6px' }}>
                <span style={{ color: '#a1a1aa', fontSize: '12px' }}>Clics en Anuncios Hoy</span>
                <span style={{ fontWeight: '800', color: '#4ade80', fontSize: '13px' }}>{overview.today_ad_clicks || 0}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 10px', background: 'rgba(255, 255, 255, 0.02)', borderRadius: '6px' }}>
                <span style={{ color: '#a1a1aa', fontSize: '12px' }}>Clics Totales ({timeRange}d)</span>
                <span style={{ fontWeight: '800', color: '#4ade80', fontSize: '13px' }}>{overview.ad_clicks || 0}</span>
              </div>
              <div style={{ fontSize: '11px', color: '#71717a', marginTop: '2px' }}>
                ℹ️ Rueda de 4 clics activa: Adsterra ⇄ Monetag alternados.
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
