// Adsterra Unified Advertising & Frequency Controller for DramaPe

// Smartlink de Adsterra (usado para el popunder limpio de 1 vez cada 24 horas y desbloqueo)
export const AD_SMARTLINK_URL = 'https://asiafilm.org/4/422780c437bf41678b7ed041ce2360a0';
export const AD_SOCIALBAR_SRC = 'https://bancadeltempoidea.org/14/6b62f8318c3bb05ca3f63b5933ef1e34';

export const BANNER_300x250_KEY = '116abd6ac1277c130835a8324f016ae8';
export const BANNER_728x90_KEY = '72b268d72853630bdffceba2f3f04daa';

const POPUNDER_STORAGE_KEY = 'dramape_pop_last_ts';
const TWENTY_FOUR_HOURS_MS = 24 * 60 * 60 * 1000;

/**
 * Control 100% nativo de Popunder (Estrictamente 1 vez cada 24 horas por usuario):
 * - NO inyecta scripts invasores externos (como aarems.org) que secuestran los clics de la ventana.
 * - Solo se ejecuta mediante un clic intencional de play del usuario.
 * - Si ya se activó en las últimas 24 horas, NO hace nada (0 pestañas, 0 interrupciones).
 * - Cero interferencia al cerrar modales, buscar doramas o navegar por el catálogo.
 */
export function checkAndTriggerPlayPopunder() {
  if (typeof window === 'undefined') return false;

  try {
    const last = localStorage.getItem(POPUNDER_STORAGE_KEY);
    const now = Date.now();

    if (last) {
      const diff = now - parseInt(last, 10);
      if (!isNaN(diff) && diff < TWENTY_FOUR_HOURS_MS) {
        // Ya vio su anuncio del día. Cero popups.
        return false;
      }
    }

    // Registrar nueva marca de tiempo de 24 horas
    localStorage.setItem(POPUNDER_STORAGE_KEY, String(now));

    // Abrir directamente el anuncio en pestaña nueva en el clic de reproducir
    // Sin listeners globales que capturen otros clics ni botones de cerrar
    window.open(AD_SMARTLINK_URL, '_blank');
    return true;
  } catch (e) {
    return false;
  }
}
