import Link from 'next/link';
import { notFound } from 'next/navigation';
import { getTitle } from '../../../../lib/api';
import Player from '../../../../components/Player';

export const dynamic = 'force-dynamic';

export async function generateMetadata({ params }) {
  const { slug, ep } = await params;
  const d = await getTitle(slug);
  if (!d) return { title: 'Episodio no encontrado | DramaPe' };
  return {
    title: `Ver ${d.title} — Capítulo ${ep} en Español HD | DramaPe`,
    description: `Mira el episodio ${ep} de ${d.title} online gratis en alta definición en DramaPe.`,
    alternates: { canonical: `/ver/${slug}/${ep}` },
    robots: { index: true, follow: true },
  };
}

export default async function VerPage({ params }) {
  const { slug, ep } = await params;
  const d = await getTitle(slug);
  if (!d) notFound();
  const total = d.total_episodes || 0;
  return (
    <Player slug={slug} ep={ep} title={d.title} total={total} />
  );
}
