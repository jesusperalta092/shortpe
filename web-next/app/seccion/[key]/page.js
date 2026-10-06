import { notFound } from 'next/navigation';
import { getCatalog, groupBySection } from '../../../lib/api';
import Header from '../../../components/Header';
import GridClient from '../../../components/GridClient';
import CatalogGrid from '../../../components/CatalogGrid';
import Footer from '../../../components/Footer';

export const dynamic = 'force-dynamic';

const LABELS = { 
  dramavibe: 'DramaVibe', 
  hotdrama: 'HotDrama', 
  drama: 'Dramas', 
  dramashorts: 'DramaShorts', 
  dramatube: 'DramaTube' 
};

const PROXY = process.env.PROXY_URL || 'http://127.0.0.1:8090';

export async function generateMetadata({ params }) {
  const { key } = await params;
  const label = LABELS[key];
  if (!label) return { title: 'Sección no encontrada | DramaPe' };
  
  const title = `${label} — Dramas Cortos y Series en Español HD | DramaPe`;
  const desc = `Explora la sección de ${label} en DramaPe. Mira los mejores dramas cortos, doramas y miniseries completas en español latino gratis en HD.`;
  
  return {
    title: `${label} — Dramas en Español`,
    description: desc,
    alternates: {
      canonical: `/seccion/${key}`,
    },
    openGraph: {
      type: 'website',
      siteName: 'DramaPe',
      title: title,
      description: desc,
      url: `/seccion/${key}`,
      locale: 'es_PE',
    },
    twitter: {
      card: 'summary_large_image',
      title: title,
      description: desc,
    },
  };
}

export default async function SeccionPage({ params }) {
  const { key } = await params;
  if (!LABELS[key]) notFound();
  const label = LABELS[key];

  // ===== Seccion 'dramavibe' (catalogo grande chartdrama) =====
  if (key === 'dramavibe') {
    let first = { items: [], total: 0, page: 1, pages: 1 };
    try {
      const r = await fetch(PROXY + '/api/dramavibe?page=1&limit=48', { cache: 'no-store' });
      if (r.ok) first = await r.json();
    } catch (e) {}
    return (
      <>
        <Header />
        <main className="con-header">
          <section className="row">
            <h2 className="row-title theme-vibe"><span className="bar" />{label} ({first.total.toLocaleString('es')})</h2>
            <CatalogGrid initial={first} apiPath="/api/dramavibe" label="DramaVibe" fireTag={false} />
          </section>
        </main>
        <Footer />
      </>
    );
  }

  // ===== Seccion 'hotdrama' (catalogo dramabox / hot) =====
  if (key === 'hotdrama') {
    let first = { items: [], total: 0, page: 1, pages: 1 };
    try {
      const r = await fetch(PROXY + '/api/hotdrama?page=1&limit=48', { cache: 'no-store' });
      if (r.ok) first = await r.json();
    } catch (e) {}
    return (
      <>
        <Header />
        <main className="con-header">
          <section className="row">
            <h2 className="row-title theme-fire"><span className="bar fire-bar" />Hot<span className="fire-text">Drama</span> ({first.total.toLocaleString('es')})</h2>
            <CatalogGrid initial={first} apiPath="/api/hotdrama" label="HotDrama" fireTag={true} />
          </section>
        </main>
        <Footer />
      </>
    );
  }

  // ===== Otras secciones: catalogo normal =====
  const cat = await getCatalog();
  const secs = groupBySection(cat);
  const items = secs[key] || [];
  const themeClass = key === 'drama' ? 'theme-drama' : (key === 'dramashorts' ? 'theme-shorts' : (key === 'dramatube' ? 'theme-tube' : ''));

  return (
    <>
      <Header stats={cat.length} />
      <main className="con-header">
        <section className="row">
          <h2 className={'row-title ' + themeClass}><span className="bar" />{label} ({items.length})</h2>
          <GridClient items={items} label={label} />
        </section>
      </main>
      <Footer catalogCount={cat.length} />
    </>
  );
}
