'use client';
import Link from 'next/link';

export default function Footer({ catalogCount = 2220 }) {
  return (
    <footer className="site-footer">
      <div className="footer-inner">
        <div className="footer-brand">
          <Link href="/" className="footer-logo" aria-label="DramaPe — Inicio">
            <img src="/logo.png" alt="DramaPe" className="logo-img" width="32" height="32" />
            <span className="logo-text">DramaPe</span>
          </Link>
          <p className="footer-tagline">
            Tu portal líder de minidramas, doramas y series cortas en español latino para Perú, México y toda Latinoamérica. Disfruta de miles de capítulos en HD 1080p gratis y sin cortes.
          </p>
          <div className="footer-badges">
            <span className="f-pill">🇵🇪 Perú & Latinoamérica</span>
            <span className="f-pill">⚡ ULTRA HD 4K / 1080p</span>
            <span className="f-pill">🚀 Carga Rápida</span>
            <span className="f-pill">✨ Estrenos Diarios</span>
          </div>
        </div>

        <div className="footer-nav">
          <div className="footer-nav-col">
            <h4>Secciones</h4>
            <Link href="/">Inicio</Link>
            <Link href="/seccion/drama">DramaVibe</Link>
            <Link href="/seccion/dramashorts">Dramas</Link>
            <Link href="/seccion/dramavibe">HotDrama</Link>
            <Link href="/seccion/hotdrama">DramaShorts</Link>
            <Link href="/seccion/dramatube">DramaTube</Link>
          </div>
          <div className="footer-nav-col">
            <h4>Catálogo DramaPe</h4>
            <span>{catalogCount.toLocaleString('es')} Dramas Activos</span>
            <span>75,000+ Capítulos</span>
            <span>100% en Español</span>
            <span>Subtítulos en Español</span>
          </div>
        </div>
      </div>

      <div className="footer-bottom">
        <p>© 2026 <b>DramaPe</b>. Todos los derechos reservados.</p>
        <p className="footer-sub">Plataforma de streaming libre de dramas cortos optimizada para celulares y alta velocidad.</p>
      </div>
    </footer>
  );
}
