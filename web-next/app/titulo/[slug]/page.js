import Link from 'next/link';
import { notFound } from 'next/navigation';
import { getTitle, getCatalog } from '../../../lib/api';

export const dynamic = 'force-dynamic';

const SITE_URL = process.env.SITE_URL || 'https://dramape.com';

// ---- SEO dinamico por titulo ----
export async function generateMetadata({ params }) {
  const { slug } = await params;
  const d = await getTitle(slug);
  if (!d) return { title: 'Título no encontrado | DramaPe' };
  
  const title = `${d.title} — Completo en Español Latino HD | DramaPe`;
  const desc = (d.description || `Mira ${d.title} completo en español con ${d.total_episodes || 'todos los'} capítulos en HD gratis en DramaPe.`).slice(0, 160);
  const posterUrl = d.poster_local ? `${SITE_URL}/${d.poster_local}` : (d.poster || `${SITE_URL}/favicon.ico`);

  return {
    title: `${d.title} — Completo en Español`,
    description: desc,
    alternates: { canonical: `/titulo/${slug}` },
    openGraph: {
      type: 'video.tv_show',
      siteName: 'DramaPe',
      title: title,
      description: desc,
      url: `/titulo/${slug}`,
      locale: 'es_PE',
      images: [
        {
          url: posterUrl,
          width: 800,
          height: 1200,
          alt: `Póster de ${d.title} en DramaPe`,
        },
      ],
    },
    twitter: {
      card: 'summary_large_image',
      title: title,
      description: desc,
      images: [posterUrl],
    },
  };
}

// ---- Pagina de detalle (SSR puro) ----
export default async function TituloPage({ params }) {
  const { slug } = await params;
  const d = await getTitle(slug);
  if (!d) notFound();

  const poster = d.poster_local ? '/' + d.poster_local : d.poster;
  const total = d.total_episodes || 0;
  const isCuk = d.source === 'cukelis';
  // claves de episodio segun la fuente
  const eps = Array.from({ length: Math.min(total, 300) }, (_, i) => {
    const n = i + 1;
    return isCuk ? ('1x' + n) : String(n);
  });

  // ---- JSON-LD estructurado (clave para GEO / motores de búsqueda) ----
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'TVSeries',
    name: d.title,
    description: d.description || '',
    image: poster ? (poster.startsWith('http') ? poster : `${SITE_URL}${poster}`) : undefined,
    numberOfEpisodes: total,
    inLanguage: 'es',
    genre: d.genres || ['Drama', 'Romance'],
    url: `${SITE_URL}/titulo/${slug}`,
    publisher: {
      '@type': 'Organization',
      name: 'DramaPe',
      url: SITE_URL,
    },
  };

  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }} />
      <header>
        <Link href="/" className="logo" aria-label="DramaPe — Inicio">
          <div className="logo-badge-container">
            <img src="/logo-icon.png" alt="DramaPe" className="logo-badge-icon" width="28" height="28" />
          </div>
          <span className="logo-text">
            <span className="logo-text-red">Drama</span><span className="logo-text-white">Pe</span>
          </span>
        </Link>
        <nav><Link href="/">← Inicio</Link></nav>
      </header>

      <main>
        <article className="detail">
          <div className="detail-hero">
            <div className="detail-poster">
              <img src={poster} alt={'Póster de ' + d.title} />
            </div>
            <div className="detail-info">
              <h1>{d.title}</h1>
              <div className="detail-meta">
                <div><span className="k">Episodios</span><span className="v">{total}</span></div>
                <div><span className="k">Género</span><span className="v">{(d.genres || []).join(' · ') || 'Drama'}</span></div>
                <div><span className="k">Idioma</span><span className="v">{d.lang === 'en' ? 'Inglés' : 'Español'}</span></div>
                <div><span className="k">Año</span><span className="v">2026</span></div>
              </div>
              <p className="detail-desc">{d.description}</p>
            </div>
          </div>

          <h2 style={{ fontSize: 18, marginBottom: 8 }}>📺 Episodios ({total})</h2>
          <div className="ep-grid">
            {eps.map((key) => (
              <a key={key} className="ep-btn" href={'/ver/' + slug + '/' + key}>
                {String(key).includes('x') ? ('T' + String(key).split('x')[0] + ' E' + String(key).split('x')[1]) : ('EP ' + key)}
              </a>
            ))}
          </div>
        </article>
      </main>
    </>
  );
}
