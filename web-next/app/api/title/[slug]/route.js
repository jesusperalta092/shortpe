const PROXY = process.env.PROXY_URL || 'http://127.0.0.1:8090';

let _cache = { t: 0, data: null };
async function catalog() {
  if (_cache.data && Date.now() - _cache.t < 60000) return _cache.data;
  const r = await fetch(PROXY + '/api/catalog', { cache: 'no-store' });
  const d = await r.json();
  _cache = { t: Date.now(), data: d };
  return d;
}

// DramaVibe: catalogo grande aparte. Busca el slug en /api/dramavibe con query exacta.
let _dvCache = new Map(); // slug -> {t, item}
async function findDramaVibe(slug) {
  const hit = _dvCache.get(slug);
  if (hit && Date.now() - hit.t < 300000) return hit.item;
  // El titulo viene del slug. Pedimos una pagina buscando por titulo no sirve; usamos endpoint dedicado.
  try {
    const r = await fetch(PROXY + '/api/dramavibe/item?slug=' + encodeURIComponent(slug), { cache: 'no-store' });
    if (!r.ok) return null;
    const d = await r.json();
    if (d && !d.error) { _dvCache.set(slug, { t: Date.now(), item: d }); return d; }
  } catch (e) {}
  return null;
}

export async function GET(req, { params }) {
  const { slug } = await params;

  // DramaVibe va por su propio carril (catalogo grande, on-demand)
  if (slug && slug.startsWith('dv-')) {
    const d = await findDramaVibe(slug);
    if (!d) return Response.json({ error: 'not found' }, { status: 404 });
    const total = d.total_episodes || 0;
    const eps = Array.from({ length: Math.min(total, 500) }, (_, i) => String(i + 1));
    return Response.json({ ...d, episodeKeys: eps }, { headers: { 'Cache-Control': 'no-store' } });
  }

  // HotDrama: su propio carril
  if (slug && slug.startsWith('hd-')) {
    try {
      const r = await fetch(PROXY + '/api/hotdrama/item?slug=' + encodeURIComponent(slug), { cache: 'no-store' });
      if (!r.ok) return Response.json({ error: 'not found' }, { status: 404 });
      const d = await r.json();
      if (!d || d.error) return Response.json({ error: 'not found' }, { status: 404 });
      const total = d.total_episodes || 0;
      const eps = Array.from({ length: Math.min(total, 500) }, (_, i) => String(i + 1));
      return Response.json({ ...d, episodeKeys: eps }, { headers: { 'Cache-Control': 'no-store' } });
    } catch (e) {
      return Response.json({ error: 'not found' }, { status: 404 });
    }
  }

  const cat = await catalog();
  const d = cat.find((x) => x.slug === slug);
  if (!d) return Response.json({ error: 'not found' }, { status: 404 });
  const total = d.total_episodes || 0;
  const isCuk = d.source === 'cukelis';
  const eps = Array.from({ length: Math.min(total, 300) }, (_, i) => (isCuk ? '1x' + (i + 1) : String(i + 1)));
  return Response.json({ ...d, episodeKeys: eps }, { headers: { 'Cache-Control': 'no-store' } });
}
