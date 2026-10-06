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

  // Cargar token previo de sessionStorage
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const saved = sessionStorage.getItem('dramape_admin_token');
      if (saved) {
        setSessionToken(saved);
      }
    }
  }, []);

  // Cargar datos cuando haya token de sesión
  useEffect(() => {
    if (!sessionToken) return;

    let isMounted = true;
    const loadMetrics = async () => {
      setLoading(true);
      const res = await fetchAdminDashboard(timeRange, sessionToken);
      if (!isMounted) return;

      if (res.unauthorized) {
        sessionStorage.removeItem('dramape_admin_token');
        setSessionToken(null);
        setAuthError('Tu sesión ha expirado o el PIN es inválido. Ingresa nuevamente.');
      } else if (res.ok) {
        setData(res);
        setLastUpdated(new Date().toLocaleTimeString());
      }
      setLoading(false);
    };

    loadMetrics();

    // Auto-actualización en vivo cada 10 segundos
    const interval = setInterval(loadMetrics, 10000);
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
  // 🔒 PANTALLA DE ACCESO CON PIN CRIPTOGRÁFICO
  // ==========================================
  if (!sessionToken) {
    return (
      <div style={{
        minHeight: '100vh',
        backgroundColor: '#07070a',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '20px',
        fontFamily: 'system-ui, -apple-system, sans-serif'
      }}>
        <div style={{
          width: '100%',
          maxWidth: '420px',
          background: 'linear-gradient(135deg, rgba(24, 24, 32, 0.95), rgba(12, 12, 16, 0.98))',
          borderRadius: '24px',
          padding: '36px 30px',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.8), 0 0 40px rgba(229, 9, 20, 0.15)',
          textAlign: 'center',
          backdropFilter: 'blur(16px)'
        }}>
          <div style={{
            width: '64px',
            height: '64px',
            margin: '0 auto 20px',
            borderRadius: '20px',
            background: 'linear-gradient(135deg, #e50914, #990000)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '28px',
            boxShadow: '0 10px 25px rgba(229, 9, 20, 0.4)'
          }}>
            🛡️
          </div>

          <h1 style={{ fontSize: '24px', fontWeight: '800', color: '#fff', margin: '0 0 8px' }}>
            Panel de Control <span style={{ color: '#e50914' }}>DramaPe</span>
          </h1>
          <p style={{ color: '#888899', fontSize: '14px', margin: '0 0 28px' }}>
            Sistema privado de métricas y telemetría en tiempo real.
          </p>

          <form onSubmit={handleLogin}>
            <div style={{ marginBottom: '18px', textAlign: 'left' }}>
              <label style={{ display: 'block', color: '#aaaaee', fontSize: '12px', fontWeight: '600', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                PIN Maestro de Seguridad
              </label>
              <input
                type="password"
                placeholder="Ingresa el PIN de seguridad"
                value={pinInput}
                onChange={(e) => setPinInput(e.target.value)}
                style={{
                  width: '100%',
                  padding: '14px 16px',
                  borderRadius: '12px',
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid rgba(255, 255, 255, 0.15)',
                  color: '#fff',
                  fontSize: '16px',
                  outline: 'none',
                  boxSizing: 'border-box',
                  textAlign: 'center',
                  letterSpacing: '0.2em'
                }}
                autoFocus
              />
            </div>

            {authError && (
              <div style={{
                background: 'rgba(229, 9, 20, 0.15)',
                border: '1px solid rgba(229, 9, 20, 0.4)',
                color: '#ff6b6b',
                padding: '10px 14px',
                borderRadius: '10px',
                fontSize: '13px',
                marginBottom: '18px',
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
                padding: '14px',
                borderRadius: '12px',
                background: authLoading ? '#666' : 'linear-gradient(135deg, #e50914, #b20710)',
                color: '#fff',
                fontWeight: '700',
                fontSize: '15px',
                border: 'none',
                cursor: authLoading ? 'not-allowed' : 'pointer',
                boxShadow: '0 8px 20px rgba(229, 9, 20, 0.35)',
                transition: 'all 0.2s ease'
              }}
            >
              {authLoading ? 'Verificando con Servidor...' : 'Desbloquear Panel'}
            </button>
          </form>

          <div style={{ marginTop: '24px' }}>
            <Link href="/" style={{ color: '#666677', fontSize: '13px', textDecoration: 'none' }}>
              ← Volver al sitio web principal
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // ==========================================
  // 📊 DASHBOARD PRINCIPAL
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
      backgroundColor: '#0a0a0f',
      color: '#f0f0f5',
      fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      padding: '24px 16px',
      boxSizing: 'border-box'
    }}>
      <div style={{ maxWidth: '1280px', margin: '0 auto' }}>
        
        {/* ENCABEZADO SUPERIOR */}
        <header style={{
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '16px',
          paddingBottom: '24px',
          borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
          marginBottom: '28px'
        }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <span style={{
                background: '#e50914',
                color: '#fff',
                fontSize: '12px',
                fontWeight: '900',
                padding: '4px 10px',
                borderRadius: '6px',
                letterSpacing: '0.05em'
              }}>PRO</span>
              <h1 style={{ fontSize: '26px', fontWeight: '900', margin: 0, letterSpacing: '-0.02em' }}>
                Panel de Analíticas <span style={{ color: '#e50914' }}>DramaPe</span>
              </h1>
            </div>
            <p style={{ color: '#888899', fontSize: '13px', margin: '6px 0 0' }}>
              Telemetría en tiempo real y métricas internas sin dependencias externas.
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
            {/* SELECTOR DE RANGO DE TIEMPO */}
            <div style={{
              display: 'inline-flex',
              background: 'rgba(255, 255, 255, 0.05)',
              borderRadius: '10px',
              padding: '4px',
              border: '1px solid rgba(255, 255, 255, 0.1)'
            }}>
              {[
                { label: 'Hoy', value: 1 },
                { label: '7 Días', value: 7 },
                { label: '30 Días', value: 30 },
                { label: '90 Días', value: 90 }
              ].map(opt => (
                <button
                  key={opt.value}
                  onClick={() => setTimeRange(opt.value)}
                  style={{
                    padding: '6px 14px',
                    borderRadius: '8px',
                    fontSize: '13px',
                    fontWeight: timeRange === opt.value ? '700' : '500',
                    background: timeRange === opt.value ? '#e50914' : 'transparent',
                    color: timeRange === opt.value ? '#fff' : '#aaa',
                    border: 'none',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease'
                  }}
                >
                  {opt.label}
                </button>
              ))}
            </div>

            <button
              onClick={handleLogout}
              style={{
                padding: '8px 14px',
                borderRadius: '8px',
                background: 'rgba(255, 255, 255, 0.08)',
                color: '#ccc',
                border: '1px solid rgba(255, 255, 255, 0.12)',
                fontSize: '13px',
                cursor: 'pointer',
                fontWeight: '600'
              }}
            >
              🔒 Salir
            </button>
          </div>
        </header>

        {/* 🔴 SECCIÓN PRINCIPAL DE TIEMPO REAL (EN VIVO AHORA) */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '18px',
          marginBottom: '28px'
        }}>
          {/* TARJETA: MIRANDO VIDEO EN VIVO */}
          <div style={{
            background: 'linear-gradient(135deg, rgba(229, 9, 20, 0.18), rgba(20, 10, 15, 0.9))',
            borderRadius: '18px',
            padding: '24px',
            border: '1px solid rgba(229, 9, 20, 0.4)',
            boxShadow: '0 10px 30px rgba(229, 9, 20, 0.2)',
            position: 'relative',
            overflow: 'hidden'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
              <span style={{ color: '#ff8888', fontSize: '13px', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Reproducción Activa
              </span>
              <span style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                background: 'rgba(229, 9, 20, 0.3)',
                color: '#ff4d4d',
                padding: '4px 10px',
                borderRadius: '20px',
                fontSize: '11px',
                fontWeight: '800'
              }}>
                <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#ff4d4d', animation: 'pulse 1.5s infinite' }}></span>
                EN VIVO
              </span>
            </div>
            <div style={{ fontSize: '42px', fontWeight: '900', color: '#fff', letterSpacing: '-0.03em' }}>
              {realtime.watching_now}
            </div>
            <div style={{ color: '#ffcccc', fontSize: '13px', marginTop: '6px' }}>
              {realtime.watching_now === 1 ? '1 persona mirando un video en este momento' : `${realtime.watching_now} personas mirando videos en este momento`}
            </div>
          </div>

          {/* TARJETA: PERSONAS NAVEGANDO EN LÍNEA */}
          <div style={{
            background: 'linear-gradient(135deg, rgba(34, 197, 94, 0.15), rgba(10, 25, 18, 0.9))',
            borderRadius: '18px',
            padding: '24px',
            border: '1px solid rgba(34, 197, 94, 0.35)',
            boxShadow: '0 10px 30px rgba(34, 197, 94, 0.12)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
              <span style={{ color: '#86efac', fontSize: '13px', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Visitantes Online
              </span>
              <span style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                background: 'rgba(34, 197, 94, 0.25)',
                color: '#4ade80',
                padding: '4px 10px',
                borderRadius: '20px',
                fontSize: '11px',
                fontWeight: '800'
              }}>
                <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#4ade80' }}></span>
                EN LÍNEA
              </span>
            </div>
            <div style={{ fontSize: '42px', fontWeight: '900', color: '#fff', letterSpacing: '-0.03em' }}>
              {realtime.online_now}
            </div>
            <div style={{ color: '#bbf7d0', fontSize: '13px', marginTop: '6px' }}>
              Personas explorando o navegando el catálogo
            </div>
          </div>

          {/* TARJETA: VISITAS ÚNICAS HOY */}
          <div style={{
            background: 'rgba(255, 255, 255, 0.03)',
            borderRadius: '18px',
            padding: '24px',
            border: '1px solid rgba(255, 255, 255, 0.08)'
          }}>
            <div style={{ color: '#8888aa', fontSize: '13px', fontWeight: '700', textTransform: 'uppercase', marginBottom: '12px' }}>
              Visitas Únicas de Hoy
            </div>
            <div style={{ fontSize: '42px', fontWeight: '900', color: '#fff' }}>
              {overview.today_visitors || 0}
            </div>
            <div style={{ color: '#888899', fontSize: '13px', marginTop: '6px' }}>
              {overview.today_plays || 0} episodios reproducidos hoy
            </div>
          </div>

          {/* TARJETA: TOTAL REPRODUCCIONES (PERIODO) */}
          <div style={{
            background: 'rgba(255, 255, 255, 0.03)',
            borderRadius: '18px',
            padding: '24px',
            border: '1px solid rgba(255, 255, 255, 0.08)'
          }}>
            <div style={{ color: '#8888aa', fontSize: '13px', fontWeight: '700', textTransform: 'uppercase', marginBottom: '12px' }}>
              Total Plays ({timeRange}d)
            </div>
            <div style={{ fontSize: '42px', fontWeight: '900', color: '#fff' }}>
              {overview.video_plays || 0}
            </div>
            <div style={{ color: '#888899', fontSize: '13px', marginTop: '6px' }}>
              {overview.unique_visitors || 0} visitantes únicos en el periodo
            </div>
          </div>
        </div>

        {/* 🎬 TRANSMISIONES ACTIVAS EN VIVO AHORA (QUÉ ESTÁN VIENDO EXACTAMENTE) */}
        <div style={{
          background: 'rgba(20, 20, 28, 0.6)',
          borderRadius: '18px',
          padding: '24px',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          marginBottom: '28px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '18px' }}>
            <h2 style={{ fontSize: '18px', fontWeight: '800', margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span>👁️</span> ¿Qué están mirando en tiempo real?
            </h2>
            <span style={{ fontSize: '12px', color: '#888' }}>
              Actualizado: {lastUpdated || 'Cargando...'}
            </span>
          </div>

          {realtime.active_streams && realtime.active_streams.length > 0 ? (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '12px' }}>
              {realtime.active_streams.map((stream, idx) => (
                <div
                  key={idx}
                  style={{
                    background: 'rgba(255, 255, 255, 0.03)',
                    border: '1px solid rgba(229, 9, 20, 0.2)',
                    borderRadius: '12px',
                    padding: '14px 16px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between'
                  }}
                >
                  <div style={{ overflow: 'hidden', paddingRight: '12px' }}>
                    <div style={{ fontWeight: '700', color: '#fff', fontSize: '14px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {stream.title}
                    </div>
                    <div style={{ fontSize: '12px', color: '#aaa', marginTop: '2px', display: 'flex', gap: '8px' }}>
                      <span style={{ color: '#e50914', fontWeight: '700' }}>Ep. {stream.ep || '1'}</span>
                      <span>•</span>
                      <span>{stream.device === 'mobile' ? '📱 Móvil' : stream.device === 'tablet' ? '📟 Tablet' : '💻 PC'}</span>
                    </div>
                  </div>
                  <div style={{
                    fontSize: '11px',
                    color: '#86efac',
                    background: 'rgba(34, 197, 94, 0.1)',
                    padding: '4px 8px',
                    borderRadius: '6px',
                    whiteSpace: 'nowrap',
                    fontWeight: '600'
                  }}>
                    hace {stream.seconds_ago}s
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '30px 20px', color: '#777', fontSize: '14px' }}>
              No hay reproducciones de video activas en este instante exacto. Los usuarios están navegando el catálogo.
            </div>
          )}
        </div>

        {/* 📈 GRÁFICO HISTÓRICO Y RANKING DE DORAMAS */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(420px, 1fr))',
          gap: '24px',
          marginBottom: '28px'
        }}>
          {/* LÍNEA DE TIEMPO / TENDENCIA */}
          <div style={{
            background: 'rgba(20, 20, 28, 0.6)',
            borderRadius: '18px',
            padding: '24px',
            border: '1px solid rgba(255, 255, 255, 0.08)'
          }}>
            <h2 style={{ fontSize: '18px', fontWeight: '800', margin: '0 0 18px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span>📈</span> Tendencia Diaria (Visitas vs Reproducciones)
            </h2>

            {timeline.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                {timeline.slice(-7).map((day, idx) => {
                  const viewPct = Math.round(((day.views || 0) / maxTimelineViews) * 100);
                  const playPct = Math.round(((day.plays || 0) / maxTimelineViews) * 100);
                  return (
                    <div key={idx}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#aaa', marginBottom: '4px' }}>
                        <span style={{ fontWeight: '600', color: '#ddd' }}>{day.date_str}</span>
                        <span>
                          <strong style={{ color: '#fff' }}>{day.visitors || 0}</strong> visitas • <strong style={{ color: '#e50914' }}>{day.plays || 0}</strong> plays
                        </span>
                      </div>
                      <div style={{ width: '100%', height: '8px', background: 'rgba(255, 255, 255, 0.06)', borderRadius: '4px', overflow: 'hidden', display: 'flex', gap: '2px' }}>
                        <div style={{ width: `${Math.min(viewPct, 100)}%`, background: '#3b82f6', borderRadius: '4px' }}></div>
                        <div style={{ width: `${Math.min(playPct, 100)}%`, background: '#e50914', borderRadius: '4px' }}></div>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: '40px 0', color: '#666' }}>
                Esperando registro de tráfico histórico...
              </div>
            )}
          </div>

          {/* TOP 10 DORAMAS MÁS VISTOS */}
          <div style={{
            background: 'rgba(20, 20, 28, 0.6)',
            borderRadius: '18px',
            padding: '24px',
            border: '1px solid rgba(255, 255, 255, 0.08)'
          }}>
            <h2 style={{ fontSize: '18px', fontWeight: '800', margin: '0 0 18px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span>🏆</span> Top 10 Doramas Más Vistos
            </h2>

            {topDramas.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {topDramas.map((drama, idx) => (
                  <div
                    key={drama.slug}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '10px 12px',
                      background: idx === 0 ? 'rgba(229, 9, 20, 0.12)' : 'rgba(255, 255, 255, 0.02)',
                      borderRadius: '10px',
                      border: idx === 0 ? '1px solid rgba(229, 9, 20, 0.3)' : '1px solid rgba(255, 255, 255, 0.04)'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', overflow: 'hidden' }}>
                      <span style={{
                        width: '24px',
                        height: '24px',
                        borderRadius: '6px',
                        background: idx === 0 ? '#e50914' : 'rgba(255, 255, 255, 0.1)',
                        color: '#fff',
                        fontSize: '12px',
                        fontWeight: '800',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        flexShrink: 0
                      }}>
                        {idx + 1}
                      </span>
                      <span style={{ fontSize: '14px', fontWeight: '600', color: '#eee', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {drama.display_title}
                      </span>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexShrink: 0 }}>
                      <span style={{ fontSize: '13px', fontWeight: '700', color: '#ff4d4d' }}>
                        {drama.play_count} plays
                      </span>
                      <Link
                        href={`/ver/${encodeURIComponent(drama.slug)}/1`}
                        target="_blank"
                        style={{
                          background: 'rgba(255, 255, 255, 0.08)',
                          color: '#fff',
                          fontSize: '11px',
                          padding: '4px 8px',
                          borderRadius: '6px',
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
              <div style={{ textAlign: 'center', padding: '40px 0', color: '#666' }}>
                No hay reproducciones registradas en este periodo.
              </div>
            )}
          </div>
        </div>

        {/* 📱 DISPOSITIVOS Y MONETIZACIÓN */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '24px'
        }}>
          {/* DISPOSITIVOS */}
          <div style={{
            background: 'rgba(20, 20, 28, 0.6)',
            borderRadius: '18px',
            padding: '24px',
            border: '1px solid rgba(255, 255, 255, 0.08)'
          }}>
            <h2 style={{ fontSize: '16px', fontWeight: '800', margin: '0 0 16px' }}>
              📱 Tráfico por Dispositivo
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {[
                { name: 'Móvil', count: devices.mobile || 0, icon: '📱', color: '#e50914' },
                { name: 'Desktop / PC', count: devices.desktop || 0, icon: '💻', color: '#3b82f6' },
                { name: 'Tablet', count: devices.tablet || 0, icon: '📟', color: '#10b981' }
              ].map(dev => {
                const pct = Math.round((dev.count / totalDevices) * 100);
                return (
                  <div key={dev.name}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', marginBottom: '4px' }}>
                      <span>{dev.icon} {dev.name}</span>
                      <span style={{ fontWeight: '700' }}>{pct}% ({dev.count})</span>
                    </div>
                    <div style={{ width: '100%', height: '8px', background: 'rgba(255, 255, 255, 0.06)', borderRadius: '4px', overflow: 'hidden' }}>
                      <div style={{ width: `${pct}%`, height: '100%', background: dev.color, borderRadius: '4px' }}></div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* MONETIZACIÓN Y ADS */}
          <div style={{
            background: 'rgba(20, 20, 28, 0.6)',
            borderRadius: '18px',
            padding: '24px',
            border: '1px solid rgba(255, 255, 255, 0.08)'
          }}>
            <h2 style={{ fontSize: '16px', fontWeight: '800', margin: '0 0 16px' }}>
              💰 Telemetría de Anuncios
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px', background: 'rgba(255, 255, 255, 0.02)', borderRadius: '10px' }}>
                <span style={{ color: '#aaa', fontSize: '14px' }}>Clics en Anuncios Hoy</span>
                <span style={{ fontWeight: '800', color: '#4ade80', fontSize: '16px' }}>{overview.today_ad_clicks || 0}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px', background: 'rgba(255, 255, 255, 0.02)', borderRadius: '10px' }}>
                <span style={{ color: '#aaa', fontSize: '14px' }}>Clics Totales ({timeRange}d)</span>
                <span style={{ fontWeight: '800', color: '#4ade80', fontSize: '16px' }}>{overview.ad_clicks || 0}</span>
              </div>
              <div style={{ fontSize: '12px', color: '#777', marginTop: '4px' }}>
                ℹ️ Rueda de 4 clics activa: Adsterra ⇄ Monetag alternados.
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
