import { getCatalog } from '../../lib/api';

export const dynamic = 'force-dynamic';

export async function GET() {
  const cat = await getCatalog();
  const lines = [
    '# DramaPe',
    '',
    '> Plataforma líder de streaming de dramas cortos, doramas y miniseries en español latino. ' + cat.length + ' títulos disponibles.',
    '',
    '## Secciones',
    '- /seccion/drama — Dramas (Catálogo Principal)',
    '- /seccion/dramavibe — DramaVibe (Tendencias)',
    '- /seccion/hotdrama — HotDrama (Exclusivos en Español)',
    '',
    '## Títulos (muestra)',
  ];
  for (const d of cat.slice(0, 100)) {
    lines.push('- [' + d.title + '](/titulo/' + d.slug + '): ' + (d.description || '').slice(0, 120));
  }
  return new Response(lines.join('\n'), { headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
}
