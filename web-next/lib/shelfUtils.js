/**
 * Utilidades para títulos e iconos de estantes y secciones (DramaTube, DramaShorts, Dramas, HotDrama).
 * Garantiza que cada subtítulo tenga exactamente 1 solo icono al inicio y ningún emoji duplicado residual.
 */
export function cleanShelfTitle(name) {
  if (!name || typeof name !== 'string') return '';
  return name
    .replace(/[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}\u{FE00}-\u{FE0F}\u{200D}]/gu, '')
    .replace(/\s+/g, ' ')
    .trim();
}
