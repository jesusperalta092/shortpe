import { getCatalog } from '../../lib/api';
import Header from '../../components/Header';
import GridClient from '../../components/GridClient';
import Footer from '../../components/Footer';

export const dynamic = 'force-dynamic';

export async function generateMetadata({ searchParams }) {
  const sp = await searchParams;
  const q = sp.q || '';
  const title = q ? `Resultados para "${q}" | DramaPe` : 'Buscar Dramas Cortos y Doramas | DramaPe';
  return {
    title,
    description: `Encuentra y mira dramas cortos, doramas y miniseries completas en español gratis en DramaPe.`,
    robots: { index: false },
  };
}

export default async function BuscarPage({ searchParams }) {
  const sp = await searchParams;
  const q = (sp.q || '').trim().toLowerCase();
  const cat = await getCatalog();
  const items = q
    ? cat.filter(d => d.title.toLowerCase().includes(q) || (d.description || '').toLowerCase().includes(q))
    : [];

  return (
    <>
      <Header stats={cat.length} />
      <main className="con-header">
        <section className="row">
          <h2 className="row-title"><span className="bar" />Resultados para “{sp.q}” ({items.length})</h2>
          {items.length === 0
            ? <p style={{ color: 'var(--muted)', padding: '20px 0' }}>Sin resultados. Probá con otra palabra.</p>
            : <GridClient items={items.slice(0, 100)} label="Resultados" />}
        </section>
      </main>
      <Footer catalogCount={cat.length} />
    </>
  );
}
