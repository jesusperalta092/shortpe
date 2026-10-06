'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';

export default function Header({ stats }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const [q, setQ] = useState('');
  const router = useRouter();
  const pathname = usePathname();

  // Cerrar menu al cambiar de ruta o presionar Escape
  useEffect(() => {
    setMenuOpen(false);
  }, [pathname]);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') setMenuOpen(false);
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const go = () => {
    const t = q.trim();
    if (t) {
      router.push('/buscar?q=' + encodeURIComponent(t));
      setMenuOpen(false);
    }
  };

  const SEC = [
    {
      href: '/',
      label: 'Inicio',
      theme: 'home',
      icon: (
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
      )
    },
    {
      href: '/seccion/dramavibe',
      label: 'DramaVibe',
      theme: 'vibe',
      icon: (
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9z"/><path d="M19 3v4M21 5h-4" strokeWidth="1.8"/></svg>
      )
    },
    {
      href: '/seccion/hotdrama',
      label: 'HotDrama',
      theme: 'fire',
      icon: (
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/></svg>
      )
    },
    {
      href: '/seccion/drama',
      label: 'Dramas',
      theme: 'drama',
      icon: (
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><rect width="20" height="15" x="2" y="7" rx="2" ry="2"/><polyline points="17 2 12 7 7 2"/></svg>
      )
    },
    {
      href: '/seccion/dramashorts',
      label: 'DramaShorts',
      theme: 'shorts',
      icon: (
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
      )
    },
    {
      href: '/seccion/dramatube',
      label: 'DramaTube',
      theme: 'tube',
      icon: (
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><rect width="20" height="15" x="2" y="4.5" rx="4"/><polygon points="10 9 15 12 10 15 10 9" fill="currentColor"/></svg>
      )
    },
  ];

  return (
    <>
      <header>
        <button
          className={`menu-btn ${menuOpen ? 'active' : ''}`}
          onClick={() => setMenuOpen(v => !v)}
          aria-label={menuOpen ? 'Cerrar menú' : 'Abrir menú'}
        >
          {menuOpen ? (
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round"><path d="M18 6 6 18M6 6l12 12"/></svg>
          ) : (
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round"><path d="M3 6h18M3 12h18M3 18h18"/></svg>
          )}
        </button>

        <Link href="/" className="logo" aria-label="DramaPe — Inicio">
          <img src="/logo.png" alt="DramaPe" className="logo-img" width="34" height="34" />
          <span className="logo-text">DramaPe</span>
        </Link>

        {/* Dropdown / Desktop Navigation */}
        <nav className={menuOpen ? 'open' : ''}>
          <div className="nav-header-mobile">
            <span className="nav-label">Navegación</span>
            <span className="nav-badge">HD</span>
          </div>

          {SEC.map(s => {
            const isActive = pathname === s.href;
            return (
              <Link
                key={s.href}
                href={s.href}
                className={(isActive ? 'active ' : '') + 'nav-theme nav-' + (s.theme || 'default')}
                onClick={() => setMenuOpen(false)}
              >
                <span className="nav-icon">{s.icon}</span>
                <span className={s.theme === 'fire' ? 'nav-text fire-text' : 'nav-text'}>{s.label}</span>
                <svg className="nav-arrow" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="m9 18 6-6-6-6"/></svg>
              </Link>
            );
          })}
        </nav>

        <div className="header-right">
          <div className="search-box">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
            <input
              value={q}
              onChange={e => setQ(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter') go(); }}
              placeholder="Buscar dramas..."
            />
          </div>
        </div>
      </header>

      {menuOpen && <div className="nav-backdrop" onClick={() => setMenuOpen(false)} />}
    </>
  );
}
