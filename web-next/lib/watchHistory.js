// ==========================================================
// DramaPe - Historial de Reproducción Ultraligero (localStorage)
// ==========================================================
// - 100% privado en el navegador del usuario (cero costo de servidor/Supabase).
// - Sobreescritura inteligente: 1 registro único por dorama (slug).
// - Límite LRU: Máximo 20 doramas para garantizar un peso fijo inferior a 5 KB.
// - Se activa tras 25 segundos de reproducción real o al finalizar el capítulo.

const STORAGE_KEY = 'dramape_watch_history';
const MAX_ITEMS = 20;

// Caché en memoria por si el usuario navega en modo ultra estricto sin acceso a storage
let memoryFallback = null;

function getRawStore() {
  if (typeof window === 'undefined') return {};
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return {};
    return JSON.parse(raw) || {};
  } catch (e) {
    return memoryFallback || {};
  }
}

function saveRawStore(store) {
  if (typeof window === 'undefined') return;
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(store));
  } catch (e) {
    memoryFallback = store;
  }

  // Notificar a otros componentes en la misma pestaña
  try {
    window.dispatchEvent(new CustomEvent('dramape_history_change', { detail: store }));
  } catch (e) {}
}

/**
 * Obtiene la lista completa de doramas en reproducción ordenados del más reciente al más antiguo.
 * @returns {Array<Object>}
 */
export function getHistory() {
  const store = getRawStore();
  const list = Object.values(store);
  return list.sort((a, b) => (b.updated_at || 0) - (a.updated_at || 0));
}

/**
 * Obtiene el progreso guardado de un dorama específico por su slug.
 * @param {string} slug 
 * @returns {Object|null} { slug, title, poster, last_ep, vistos, total_eps, updated_at }
 */
export function getDoramaProgress(slug) {
  if (!slug) return null;
  const store = getRawStore();
  return store[slug] || null;
}

/**
 * Verifica si un episodio específico ya fue visto por el usuario.
 * @param {string} slug 
 * @param {string|number} ep 
 * @returns {boolean}
 */
export function isEpisodeWatched(slug, ep) {
  const item = getDoramaProgress(slug);
  if (!item || !Array.isArray(item.vistos)) return false;
  const epStr = String(ep).trim();
  return item.vistos.some(v => String(v).trim() === epStr);
}

/**
 * Registra o actualiza el progreso de un dorama tras 25 segundos de reproducción.
 * Sobreescribe el último episodio y agrega a la lista de vistos sin duplicar doramas.
 */
export function recordProgress({ slug, ep, title, poster, total_eps, last_time = 0, duration = 0 }) {
  if (!slug || !ep) return;

  const store = getRawStore();
  const existing = store[slug] || {};
  const epStr = String(ep).trim();

  // Mantener lista limpia y sin duplicados de episodios vistos
  const currentVistos = Array.isArray(existing.vistos) ? [...existing.vistos] : [];
  if (!currentVistos.includes(epStr)) {
    currentVistos.push(epStr);
  }

  // Normalizar poster
  let cleanPoster = poster || existing.poster || '';
  if (cleanPoster && cleanPoster.startsWith('http://localhost')) {
    cleanPoster = '';
  }

  let timeToSave = Math.floor(last_time || 0);
  if (timeToSave <= 0 && existing.last_ep === epStr && existing.last_time > 0) {
    timeToSave = existing.last_time;
  }

  // Actualizar entrada única para este slug
  store[slug] = {
    slug,
    title: title || existing.title || slug,
    poster: cleanPoster,
    last_ep: epStr,
    last_time: timeToSave,
    duration: Math.floor(duration || existing.duration || 0),
    vistos: currentVistos,
    total_eps: total_eps || existing.total_eps || 0,
    updated_at: Date.now()
  };

  // Poda LRU (Mantener solo los 20 más recientes para ahorrar espacio)
  const entries = Object.entries(store);
  if (entries.length > MAX_ITEMS) {
    entries.sort((a, b) => (b[1].updated_at || 0) - (a[1].updated_at || 0));
    const trimmedStore = {};
    for (let i = 0; i < MAX_ITEMS; i++) {
      trimmedStore[entries[i][0]] = entries[i][1];
    }
    saveRawStore(trimmedStore);
    return;
  }

  saveRawStore(store);
}

/**
 * Guarda periódicamente el segundo exacto de reproducción mientras el usuario mira el video.
 */
export function updateWatchTime(slug, ep, time, duration) {
  if (!slug || !ep) return;
  const store = getRawStore();
  const item = store[slug];
  if (!item) return;

  const epStr = String(ep).trim();
  const sec = Math.floor(time || 0);
  const dur = Math.floor(duration || item.duration || 0);

  // Si está a punto de terminar (>95% o a menos de 4s del final), marcar como 0 para que empiece desde el inicio
  if (dur > 0 && sec >= dur - 4) {
    item.last_time = 0;
  } else {
    item.last_time = sec;
  }
  item.duration = dur;
  item.last_ep = epStr;
  item.updated_at = Date.now();

  saveRawStore(store);
}

/**
 * Permite al usuario eliminar un dorama de su fila "Continuar Viendo".
 * @param {string} slug 
 */
export function removeFromHistory(slug) {
  if (!slug) return;
  const store = getRawStore();
  if (store[slug]) {
    delete store[slug];
    saveRawStore(store);
  }
}

/**
 * Limpia todo el historial.
 */
export function clearAllHistory() {
  saveRawStore({});
}
