// Cliente del backend Python (proxy). Server-side usa localhost, cliente usa rutas relativas.
const PROXY = process.env.PROXY_URL || 'http://127.0.0.1:8090';

/** Trae el catalogo completo (server-side). */
export async function getCatalog() {
  try {
    const res = await fetch(PROXY + '/api/catalog', { cache: 'no-store' });
    if (res.ok) {
      return await res.json();
    }
  } catch (e) {}
  return [];
}

/** Trae items de HotDrama (server-side). */
export async function getHotDrama(limit = 24) {
  try {
    const res = await fetch(`${PROXY}/api/hotdrama?page=1&limit=${limit}`, { cache: 'no-store' });
    if (res.ok) {
      const data = await res.json();
      return data.items || [];
    }
  } catch (e) {}
  return [];
}

/** Trae items de DramaVibe (server-side). */
export async function getDramaVibe(limit = 24) {
  try {
    const res = await fetch(`${PROXY}/api/dramavibe?page=1&limit=${limit}`, { cache: 'no-store' });
    if (res.ok) {
      const data = await res.json();
      return data.items || [];
    }
  } catch (e) {}
  return [];
}

/** Trae un titulo por slug (server-side). */
export async function getTitle(slug) {
  // DramaVibe vive en su propio catalogo (grande, aparte)
  if (slug && slug.startsWith('dv-')) {
    try {
      const r = await fetch(PROXY + '/api/dramavibe/item?slug=' + encodeURIComponent(slug), { cache: 'no-store' });
      if (r.ok) {
        const d = await r.json();
        if (d && !d.error) return d;
      }
    } catch (e) {}
    return null;
  }
  // HotDrama
  if (slug && slug.startsWith('hd-')) {
    try {
      const r = await fetch(PROXY + '/api/hotdrama/item?slug=' + encodeURIComponent(slug), { cache: 'no-store' });
      if (r.ok) {
        const d = await r.json();
        if (d && !d.error) return d;
      }
    } catch (e) {}
    return null;
  }
  const cat = await getCatalog();
  return cat.find((d) => d.slug === slug) || null;
}

/** Trae la lista de secciones disponibles. */
export function groupBySection(cat) {
  const out = {};
  for (const d of cat) {
    const s = d.section || 'drama';
    (out[s] = out[s] || []).push(d);
  }
  return out;
}

/** URL publica del backend para el navegador (via rewrite). */
export function clientProxy() {
  return '';
}
