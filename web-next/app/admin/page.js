'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';

export default function AdminDashboardPage() {
  const [authKey, setAuthKey] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [passInput, setPassInput] = useState('');
  const [authError, setAuthError] = useState('');
  
  const [timeRange, setTimeRange] = useState(7);
  const [loading, setLoading] = useState(true);
  const [metrics, setMetrics] = useState(null);
  const [lastRefreshed, setLastRefreshed] = useState(null);

  // Clave de acceso administrativa por defecto
  const MASTER_KEY = 'dramape2026';

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const saved = sessionStorage.getItem('dramape_admin_token');
      if (saved === MASTER_KEY) {
        setIsAuthenticated(true);
      }
    }
  }, []);

  const handleLogin = (e) => {
    e.preventDefault();
    if (passInput.trim() === MASTER_KEY) {
      setIsAuthenticated(true);
      setAuthError('');
      if (typeof window !== 'undefined') {
        sessionStorage.setItem('dramape_admin_token', MASTER_KEY);
      }
    } else {
      setAuthError('Clave de acceso incorrecta');
    }
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    if (typeof window !== 'undefined') {
      sessionStorage.removeItem('dramape_admin_token');
    }
  };

  const fetchMetrics = async (days = timeRange) => {
    setLoading(true);
    try {
      const res = await fetch(`/api/analytics/dashboard?days=${days}`, { cache: 'no-store' });
      if (res.ok) {
        const data = await res.json();
        if (data.ok) {
          setMetrics(data);
          setLastRefreshed(new Date().toLocaleTimeString());
        }
      }
    } catch (e) {
      console.error('Error fetching analytics metrics:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      fetchMetrics(timeRange);
      const interval = setInterval(() => fetchMetrics(timeRange), 30000); // Refresco auto cada 30s
      return () => clearInterval(interval);
    }
  }, [isAuthenticated, timeRange]);

  // Pantalla de Bloqueo / Login PIN
  if (!isAuthenticated) {
    return (
      <div style={styles.loginWrapper}>
        <div style={styles.loginCard}>
          <div style={styles.logoBadge}>
            <span style={{ color: '#E50914', fontWeight: 900, fontSize: 26, letterSpacing: -1 }}>Drama<span style={{ color: '#fff' }}>Pe</span></span>
            <span style={styles.adminTag}>PANEL ADMIN</span>
          </div>
          <h2 style={{ fontSize: 20, color: '#fff', margin: '16px 0 6px', fontWeight: 700 }}>Acceso a Estadísticas</h2>
          <p style={{ color: '#8c8c99', fontSize: 13, marginBottom: 24, lineHeight: 1.4 }}>
            Ingresa tu clave de administración para visualizar el tráfico y métricas en vivo.
          </p>
          <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            <input
              type="password"
              placeholder="Clave de acceso (ej: dramape2026)"
              value={passInput}
              onChange={(e) => setPassInput(e.target.value)}
              style={styles.loginInput}
              autoFocus
            />
            {authError && <div style={styles.errorText}>⚠️ {authError}</div>}
            <button type="submit" style={styles.loginBtn}>
              Desbloquear Dashboard 🚀
            </button>
          </form>
          <div style={{ marginTop: 24, fontSize: 12, color: '#555', textAlign: 'center' }}>
            DramaPe Analytics Engine v1.0 · SQLite Embedded
          </div>
        </div>
      </div>
    );
  }

  const overview = metrics?.overview || {
    unique_visitors: 0,
    today_visitors: 0,
    pageviews: 0,
    video_plays: 0,
    today_plays: 0,
    ad_clicks: 0,
    today_ad_clicks: 0,
    live_users: 1
  };

  const devices = metrics?.devices || { mobile: 0, desktop: 0, tablet: 0 };
  const totalDevices = (devices.mobile + devices.desktop + devices.tablet) || 1;
  const mobilePct = Math.round((devices.mobile / totalDevices) * 100);
  const desktopPct = Math.round((devices.desktop / totalDevices) * 100);
  const tabletPct = Math.round((devices.tablet / totalDevices) * 100);

  const topDramas = metrics?.top_dramas || [];
  const timeline = metrics?.timeline || [];
  const maxViews = Math.max(...timeline.map(t => Math.max(t.views || 0, t.plays || 0)), 1);

  return (
    <div style={styles.container}>
      {/* Header Superior */}
      <header style={styles.header}>
        <div style={styles.headerLeft}>
          <Link href="/" style={styles.backHomeBtn}>
            ← Volver a DramaPe
          </Link>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{ color: '#E50914', fontWeight: 900, fontSize: 24, letterSpacing: -1 }}>
              Drama<span style={{ color: '#fff' }}>Pe</span>
            </span>
            <span style={styles.badgeLive}>
              <span style={styles.livePulse} /> EN VIVO ({overview.live_users} online)
            </span>
          </div>
        </div>

        <div style={styles.headerRight}>
          <div style={styles.rangeSelector}>
            {[
              { label: 'Hoy', days: 1 },
              { label: '7 Días', days: 7 },
              { label: '30 Días', days: 30 }
            ].map(tab => (
              <button
                key={tab.days}
                onClick={() => setTimeRange(tab.days)}
                style={{
                  ...styles.rangeBtn,
                  ...(timeRange === tab.days ? styles.rangeBtnActive : {})
                }}
              >
                {tab.label}
              </button>
            ))}
          </div>

          <button onClick={() => fetchMetrics(timeRange)} style={styles.refreshBtn} title="Refrescar métricas">
            🔄 {lastRefreshed ? `Actualizado ${lastRefreshed}` : 'Refrescar'}
          </button>

          <button onClick={handleLogout} style={styles.logoutBtn} title="Cerrar sesión">
            🔒 Salir
          </button>
        </div>
      </header>

      {/* Grid de Métricas Principales */}
      <div style={styles.statsGrid}>
        {/* Tarjeta 1: Visitantes Únicos */}
        <div style={{ ...styles.card, ...styles.cardGlowRed }}>
          <div style={styles.cardHeader}>
            <span style={styles.cardTitle}>👥 VISITANTES ÚNICOS</span>
            <span style={styles.pillGreen}>+{overview.today_visitors} hoy</span>
          </div>
          <div style={styles.cardValue}>{overview.unique_visitors.toLocaleString()}</div>
          <div style={styles.cardSub}>Personas individuales registradas</div>
        </div>

        {/* Tarjeta 2: Reproducciones de Video */}
        <div style={{ ...styles.card, ...styles.cardGlowPurple }}>
          <div style={styles.cardHeader}>
            <span style={styles.cardTitle}>🎬 REPRODUCCIONES DE VIDEO</span>
            <span style={styles.pillGreen}>+{overview.today_plays} hoy</span>
          </div>
          <div style={styles.cardValue}>{overview.video_plays.toLocaleString()}</div>
          <div style={styles.cardSub}>Episodios reproducidos con éxito</div>
        </div>

        {/* Tarjeta 3: Vistas de Página (Pageviews) */}
        <div style={{ ...styles.card, ...styles.cardGlowBlue }}>
          <div style={styles.cardHeader}>
            <span style={styles.cardTitle}>👁️ PÁGINAS VISTAS</span>
            <span style={styles.pillMuted}>Total acumulado</span>
          </div>
          <div style={styles.cardValue}>{overview.pageviews.toLocaleString()}</div>
          <div style={styles.cardSub}>Navegación en catálogo y secciones</div>
        </div>

        {/* Tarjeta 4: Monetización y Clics en Ads */}
        <div style={{ ...styles.card, ...styles.cardGlowAmber }}>
          <div style={styles.cardHeader}>
            <span style={styles.cardTitle}>💰 CLICS EN ANUNCIOS</span>
            <span style={styles.pillGreen}>+{overview.today_ad_clicks} hoy</span>
          </div>
          <div style={styles.cardValue}>{overview.ad_clicks.toLocaleString()}</div>
          <div style={styles.cardSub}>Adsterra & Monetag activaciones</div>
        </div>
      </div>

      {/* Sección Central: Gráfica de Tráfico + Distribución de Dispositivos */}
      <div style={styles.middleGrid}>
        {/* Gráfica de Líneas / Barras Diarias */}
        <div style={{ ...styles.card, flex: 2 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
            <div>
              <h3 style={styles.sectionHeading}>📈 Evolución de Tráfico y Streaming</h3>
              <p style={{ color: '#888', fontSize: 13 }}>Visitantes vs Reproducciones por día</p>
            </div>
            <div style={{ display: 'flex', gap: 12, fontSize: 12 }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: 6, color: '#4ade80' }}>
                <span style={{ width: 10, height: 10, borderRadius: 2, background: '#4ade80' }} /> Visitas
              </span>
              <span style={{ display: 'flex', alignItems: 'center', gap: 6, color: '#e50914' }}>
                <span style={{ width: 10, height: 10, borderRadius: 2, background: '#e50914' }} /> Reproducciones
              </span>
            </div>
          </div>

          {timeline.length === 0 ? (
            <div style={styles.emptyBox}>No hay suficiente historial de eventos aún. Los datos se graficarán conforme entren visitantes.</div>
          ) : (
            <div style={styles.chartContainer}>
              {timeline.map((item, idx) => {
                const viewsHeight = Math.max(12, Math.round(((item.views || 0) / maxViews) * 160));
                const playsHeight = Math.max(8, Math.round(((item.plays || 0) / maxViews) * 160));
                return (
                  <div key={idx} style={styles.chartCol}>
                    <div style={styles.barsWrap}>
                      <div
                        style={{ ...styles.barViews, height: `${viewsHeight}px` }}
                        title={`${item.date_str}: ${item.views || 0} visitas`}
                      />
                      <div
                        style={{ ...styles.barPlays, height: `${playsHeight}px` }}
                        title={`${item.date_str}: ${item.plays || 0} reproducciones`}
                      />
                    </div>
                    <span style={styles.barLabel}>{item.date_str.slice(5)}</span>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Distribución por Dispositivo */}
        <div style={{ ...styles.card, flex: 1 }}>
          <h3 style={styles.sectionHeading}>📱 Dispositivos de Usuarios</h3>
          <p style={{ color: '#888', fontSize: 13, marginBottom: 20 }}>Porcentaje según el navegador</p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {/* Móvil */}
            <div>
              <div style={styles.deviceRow}>
                <span>📱 Celulares (Móvil)</span>
                <span style={{ fontWeight: 700, color: '#fff' }}>{mobilePct}% ({devices.mobile})</span>
              </div>
              <div style={styles.progressBarBg}>
                <div style={{ ...styles.progressBarFill, width: `${mobilePct}%`, background: '#E50914' }} />
              </div>
            </div>

            {/* Computadora */}
            <div>
              <div style={styles.deviceRow}>
                <span>💻 Computadoras (Desktop)</span>
                <span style={{ fontWeight: 700, color: '#fff' }}>{desktopPct}% ({devices.desktop})</span>
              </div>
              <div style={styles.progressBarBg}>
                <div style={{ ...styles.progressBarFill, width: `${desktopPct}%`, background: '#3b82f6' }} />
              </div>
            </div>

            {/* Tablet */}
            <div>
              <div style={styles.deviceRow}>
                <span>📟 Tablets / iPads</span>
                <span style={{ fontWeight: 700, color: '#fff' }}>{tabletPct}% ({devices.tablet})</span>
              </div>
              <div style={styles.progressBarBg}>
                <div style={{ ...styles.progressBarFill, width: `${tabletPct}%`, background: '#a855f7' }} />
              </div>
            </div>
          </div>

          <div style={styles.infoPillBox}>
            ⚡ <b>Optimización activa:</b> El 100% de los streams y posters están enrutados por Cloudflare Edge Cache.
          </div>
        </div>
      </div>

      {/* Top 10 Doramas Más Vistos */}
      <div style={{ ...styles.card, marginTop: 24 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <div>
            <h3 style={styles.sectionHeading}>🔥 Top 10 Doramas Más Reproducidos</h3>
            <p style={{ color: '#888', fontSize: 13 }}>Los títulos con mayor audiencia en la plataforma</p>
          </div>
          <span style={styles.pillMuted}>{topDramas.length} títulos rankeados</span>
        </div>

        {topDramas.length === 0 ? (
          <div style={styles.emptyBox}>Aún no hay reproducciones registradas. En cuanto los usuarios vean episodios, aparecerán en el ranking.</div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={styles.table}>
              <thead>
                <tr style={styles.tableHeaderRow}>
                  <th style={styles.th}>RANK</th>
                  <th style={styles.th}>DORAMA</th>
                  <th style={styles.th}>SLUG / ID</th>
                  <th style={{ ...styles.th, textAlign: 'right' }}>REPRODUCCIONES</th>
                  <th style={{ ...styles.th, textAlign: 'center' }}>ACCIONES</th>
                </tr>
              </thead>
              <tbody>
                {topDramas.map((drama, idx) => (
                  <tr key={drama.slug} style={styles.tableRow}>
                    <td style={{ ...styles.td, fontWeight: 900, color: idx === 0 ? '#facc15' : idx === 1 ? '#e2e8f0' : idx === 2 ? '#f97316' : '#666' }}>
                      #{idx + 1}
                    </td>
                    <td style={{ ...styles.td, fontWeight: 600, color: '#fff' }}>
                      {drama.display_title}
                    </td>
                    <td style={{ ...styles.td, color: '#888', fontFamily: 'monospace', fontSize: 12 }}>
                      {drama.slug}
                    </td>
                    <td style={{ ...styles.td, textAlign: 'right', fontWeight: 700, color: '#4ade80' }}>
                      {drama.play_count.toLocaleString()} plays
                    </td>
                    <td style={{ ...styles.td, textAlign: 'center' }}>
                      <Link href={`/ver/${drama.slug}/1`} target="_blank" style={styles.viewDramaBtn}>
                        ▶ Ver Stream
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <footer style={styles.footer}>
        <span>DramaPe Analytics Engine · Persistencia Local SQLite · Cero dependencias externas</span>
      </footer>
    </div>
  );
}

const styles = {
  container: {
    minHeight: '100vh',
    background: '#0a0a0f',
    color: '#e4e4e7',
    fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    padding: '24px 32px 48px',
    maxWidth: 1400,
    margin: '0 auto',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    flexWrap: 'wrap',
    gap: 16,
    paddingBottom: 24,
    borderBottom: '1px solid rgba(255,255,255,0.08)',
    marginBottom: 28,
  },
  headerLeft: {
    display: 'flex',
    flexDirection: 'column',
    gap: 8,
  },
  backHomeBtn: {
    color: '#888',
    textDecoration: 'none',
    fontSize: 13,
    transition: 'color 0.2s',
  },
  badgeLive: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: 6,
    background: 'rgba(34, 197, 94, 0.15)',
    border: '1px solid rgba(34, 197, 94, 0.3)',
    color: '#4ade80',
    padding: '4px 10px',
    borderRadius: 20,
    fontSize: 12,
    fontWeight: 700,
  },
  livePulse: {
    width: 8,
    height: 8,
    borderRadius: '50%',
    background: '#22c55e',
    boxShadow: '0 0 8px #22c55e',
  },
  headerRight: {
    display: 'flex',
    alignItems: 'center',
    gap: 12,
    flexWrap: 'wrap',
  },
  rangeSelector: {
    display: 'flex',
    background: 'rgba(255,255,255,0.05)',
    borderRadius: 8,
    padding: 3,
    border: '1px solid rgba(255,255,255,0.1)',
  },
  rangeBtn: {
    background: 'transparent',
    border: 'none',
    color: '#aaa',
    padding: '6px 14px',
    fontSize: 13,
    fontWeight: 600,
    borderRadius: 6,
    cursor: 'pointer',
    transition: 'all 0.2s',
  },
  rangeBtnActive: {
    background: '#E50914',
    color: '#fff',
    boxShadow: '0 2px 8px rgba(229,9,20,0.4)',
  },
  refreshBtn: {
    background: 'rgba(255,255,255,0.08)',
    border: '1px solid rgba(255,255,255,0.12)',
    color: '#ddd',
    padding: '8px 14px',
    fontSize: 13,
    borderRadius: 8,
    cursor: 'pointer',
    fontWeight: 600,
  },
  logoutBtn: {
    background: 'rgba(239, 68, 68, 0.12)',
    border: '1px solid rgba(239, 68, 68, 0.3)',
    color: '#f87171',
    padding: '8px 14px',
    fontSize: 13,
    borderRadius: 8,
    cursor: 'pointer',
    fontWeight: 600,
  },
  statsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
    gap: 20,
    marginBottom: 28,
  },
  card: {
    background: 'rgba(18, 18, 26, 0.85)',
    backdropFilter: 'blur(16px)',
    border: '1px solid rgba(255,255,255,0.08)',
    borderRadius: 14,
    padding: 22,
    boxShadow: '0 8px 32px rgba(0,0,0,0.3)',
  },
  cardGlowRed: {
    borderLeft: '4px solid #E50914',
  },
  cardGlowPurple: {
    borderLeft: '4px solid #a855f7',
  },
  cardGlowBlue: {
    borderLeft: '4px solid #3b82f6',
  },
  cardGlowAmber: {
    borderLeft: '4px solid #f59e0b',
  },
  cardHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  cardTitle: {
    fontSize: 11,
    fontWeight: 800,
    letterSpacing: 1.1,
    color: '#888',
  },
  cardValue: {
    fontSize: 32,
    fontWeight: 900,
    color: '#fff',
    letterSpacing: -0.5,
  },
  cardSub: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
  },
  pillGreen: {
    background: 'rgba(34,197,94,0.15)',
    color: '#4ade80',
    fontSize: 11,
    fontWeight: 700,
    padding: '2px 8px',
    borderRadius: 12,
  },
  pillMuted: {
    background: 'rgba(255,255,255,0.08)',
    color: '#aaa',
    fontSize: 11,
    fontWeight: 600,
    padding: '2px 8px',
    borderRadius: 12,
  },
  middleGrid: {
    display: 'flex',
    gap: 20,
    flexWrap: 'wrap',
  },
  sectionHeading: {
    fontSize: 17,
    fontWeight: 700,
    color: '#fff',
    margin: 0,
  },
  chartContainer: {
    display: 'flex',
    alignItems: 'flex-end',
    justifyContent: 'space-between',
    gap: 12,
    height: 190,
    paddingTop: 10,
    borderBottom: '1px solid rgba(255,255,255,0.08)',
  },
  chartCol: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: 6,
    flex: 1,
  },
  barsWrap: {
    display: 'flex',
    gap: 4,
    alignItems: 'flex-end',
    height: 160,
  },
  barViews: {
    width: 14,
    background: 'linear-gradient(180deg, #4ade80, #16a34a)',
    borderRadius: '4px 4px 0 0',
    transition: 'height 0.3s ease',
  },
  barPlays: {
    width: 14,
    background: 'linear-gradient(180deg, #E50914, #991b1b)',
    borderRadius: '4px 4px 0 0',
    transition: 'height 0.3s ease',
  },
  barLabel: {
    fontSize: 11,
    color: '#777',
    fontWeight: 600,
  },
  deviceRow: {
    display: 'flex',
    justifyContent: 'space-between',
    fontSize: 13,
    marginBottom: 6,
    color: '#ccc',
  },
  progressBarBg: {
    height: 8,
    background: 'rgba(255,255,255,0.08)',
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressBarFill: {
    height: '100%',
    borderRadius: 4,
    transition: 'width 0.4s ease',
  },
  infoPillBox: {
    marginTop: 24,
    background: 'rgba(255,255,255,0.04)',
    border: '1px solid rgba(255,255,255,0.08)',
    borderRadius: 8,
    padding: '12px 14px',
    fontSize: 12,
    color: '#aaa',
    lineHeight: 1.4,
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
    fontSize: 13,
  },
  tableHeaderRow: {
    borderBottom: '1px solid rgba(255,255,255,0.1)',
  },
  th: {
    padding: '10px 12px',
    textAlign: 'left',
    color: '#888',
    fontSize: 11,
    fontWeight: 700,
    letterSpacing: 0.5,
  },
  tableRow: {
    borderBottom: '1px solid rgba(255,255,255,0.04)',
    transition: 'background 0.2s',
  },
  td: {
    padding: '12px',
  },
  viewDramaBtn: {
    display: 'inline-block',
    background: 'rgba(229, 9, 20, 0.15)',
    border: '1px solid rgba(229, 9, 20, 0.3)',
    color: '#E50914',
    textDecoration: 'none',
    fontSize: 12,
    fontWeight: 700,
    padding: '4px 10px',
    borderRadius: 6,
    transition: 'all 0.2s',
  },
  emptyBox: {
    padding: '36px 16px',
    textAlign: 'center',
    color: '#777',
    fontSize: 13,
  },
  footer: {
    marginTop: 40,
    textAlign: 'center',
    color: '#555',
    fontSize: 12,
    borderTop: '1px solid rgba(255,255,255,0.05)',
    paddingTop: 20,
  },
  loginWrapper: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: 'radial-gradient(circle at center, #1a0808 0%, #08080c 100%)',
    padding: 20,
  },
  loginCard: {
    width: '100%',
    maxWidth: 400,
    background: 'rgba(18, 18, 26, 0.95)',
    backdropFilter: 'blur(20px)',
    border: '1px solid rgba(255,255,255,0.1)',
    borderRadius: 16,
    padding: 32,
    boxShadow: '0 16px 48px rgba(0,0,0,0.5)',
    textAlign: 'center',
  },
  logoBadge: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: 8,
    marginBottom: 8,
  },
  adminTag: {
    background: '#E50914',
    color: '#fff',
    fontSize: 10,
    fontWeight: 900,
    padding: '2px 6px',
    borderRadius: 4,
    letterSpacing: 0.5,
  },
  loginInput: {
    background: 'rgba(255,255,255,0.06)',
    border: '1px solid rgba(255,255,255,0.15)',
    borderRadius: 8,
    padding: '12px 16px',
    fontSize: 14,
    color: '#fff',
    outline: 'none',
    textAlign: 'center',
    letterSpacing: 1,
  },
  loginBtn: {
    background: 'linear-gradient(135deg, #E50914, #B81D24)',
    border: 'none',
    borderRadius: 8,
    color: '#fff',
    padding: '12px 16px',
    fontSize: 14,
    fontWeight: 700,
    cursor: 'pointer',
    boxShadow: '0 4px 16px rgba(229,9,20,0.4)',
    transition: 'opacity 0.2s',
  },
  errorText: {
    color: '#f87171',
    fontSize: 12,
    fontWeight: 600,
  },
};
