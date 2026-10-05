'use client';
import { useEffect } from 'react';

export default function Guard() {
  useEffect(() => {
    // 1) Bloquear clic derecho
    const noCtx = (e) => e.preventDefault();
    document.addEventListener('contextmenu', noCtx);

    // 2) Bloquear arrastrar imagenes/video
    const noDrag = (e) => { if (e.target.tagName === 'IMG' || e.target.tagName === 'VIDEO') e.preventDefault(); };
    document.addEventListener('dragstart', noDrag);

    // 3) Bloquear atajos de guardado / fuente / devtools
    const noKeys = (e) => {
      const k = e.key.toLowerCase();
      if ((e.ctrlKey && ['s', 'u', 'p'].includes(k))) e.preventDefault();
      if ((e.ctrlKey && e.shiftKey && ['i', 'j', 'c'].includes(k)) || e.key === 'F12') e.preventDefault();
      if ((e.ctrlKey && e.shiftKey && ['s', 'e'].includes(k))) e.preventDefault(); // guardar como / network
    };
    document.addEventListener('keydown', noKeys);

    // 4) Bloquear copiar/pegar de contenido (excepto inputs)
    const noCopy = (e) => { if (!e.target.closest('input, textarea')) e.preventDefault(); };
    document.addEventListener('copy', noCopy);
    document.addEventListener('cut', noCopy);

    // 5) Bloquear seleccion de texto
    const noSelect = (e) => { if (!e.target.closest('input, textarea')) e.preventDefault(); };
    document.addEventListener('selectstart', noSelect);

    // 6) Bloquear iframe embedding (evita que otros sitios te embeban)
    try {
      if (window.top !== window.self) {
        window.top.location = window.self.location;
      }
    } catch (e) {}

    return () => {
      document.removeEventListener('contextmenu', noCtx);
      document.removeEventListener('dragstart', noDrag);
      document.removeEventListener('keydown', noKeys);
      document.removeEventListener('copy', noCopy);
      document.removeEventListener('cut', noCopy);
      document.removeEventListener('selectstart', noSelect);
    };
  }, []);
  return null;
}
