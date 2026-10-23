// Adsterra Unified Advertising & Frequency Controller for DramaPe

export const AD_POPUNDER_SRC = 'https://aarems.org/1/6096dad751c2b0243362aa0d3d0501f4';
export const AD_SOCIALBAR_SRC = 'https://bancadeltempoidea.org/14/6b62f8318c3bb05ca3f63b5933ef1e34';

export const BANNER_300x250_KEY = '116abd6ac1277c130835a8324f016ae8';
export const BANNER_728x90_KEY = '72b268d72853630bdffceba2f3f04daa';

const POPUNDER_STORAGE_KEY = 'dramape_pop_last_ts';
const TWENTY_FOUR_HOURS_MS = 24 * 60 * 60 * 1000;

/**
 * Control inteligente de Popunder:
 * Solo se activa en el PRIMER PLAY del día (1 vez cada 24 horas por usuario).
 * Mientras navega por el catálogo o busca doramas, el popunder permanece 100% inactivo.
 */
export function checkAndTriggerPlayPopunder() {
  if (typeof window === 'undefined') return false;

  try {
    const last = localStorage.getItem(POPUNDER_STORAGE_KEY);
    const now = Date.now();

    if (last) {
      const diff = now - parseInt(last, 10);
      if (!isNaN(diff) && diff < TWENTY_FOUR_HOURS_MS) {
        // Ya vio su único popunder del día. No molestamos al usuario.
        return false;
      }
    }

    // Registrar nueva marca de tiempo de 24 horas
    localStorage.setItem(POPUNDER_STORAGE_KEY, String(now));

    // Inyectar el script de Adsterra Popunder solo para este primer play
    const existing = document.getElementById('adsterra-popunder-script');
    if (!existing) {
      const script = document.createElement('script');
      script.id = 'adsterra-popunder-script';
      script.setAttribute('data-cfasync', 'false');
      script.src = AD_POPUNDER_SRC;
      script.async = true;
      document.head.appendChild(script);
    }

    return true;
  } catch (e) {
    return false;
  }
}
