'use client';
import { useEffect, useRef } from 'react';

/**
 * Componente de Banner Adsterra aislado mediante iframe sandbox.
 * Evita bloqueos de document.write() en React/Next.js y aísla atOptions de colisiones.
 * Soporta callback onBlocked para auto-colapsar el espacio si un adblocker (como Brave) bloquea el anuncio.
 */
export default function AdsterraBanner({ zoneKey, width = 300, height = 250, className = '', onBlocked }) {
  const containerRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current || !zoneKey) return;

    // Escuchar si el adblocker bloquea el recurso
    const handleMsg = (e) => {
      if (e.data && e.data.type === 'adsterra_blocked' && e.data.key === zoneKey) {
        if (onBlocked) onBlocked();
      }
    };
    window.addEventListener('message', handleMsg);

    const iframe = document.createElement('iframe');
    iframe.width = String(width);
    iframe.height = String(height);
    iframe.style.border = 'none';
    iframe.style.overflow = 'hidden';
    iframe.style.background = 'transparent';
    iframe.style.display = 'block';
    iframe.setAttribute('scrolling', 'no');
    iframe.setAttribute('title', 'Anuncio publicitario');
    iframe.setAttribute('loading', 'lazy');

    const html = `
      <!DOCTYPE html>
      <html>
        <head>
          <meta charset="utf-8">
          <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            html, body {
              width: 100%;
              height: 100%;
              overflow: hidden;
              background: transparent;
              display: flex;
              align-items: center;
              justify-content: center;
            }
          </style>
        </head>
        <body>
          <script type="text/javascript">
            atOptions = {
              'key' : '${zoneKey}',
              'format' : 'iframe',
              'height' : ${height},
              'width' : ${width},
              'params' : {}
            };
          </script>
          <script 
            type="text/javascript" 
            src="https://bancadeltempoidea.org/22/${zoneKey}"
            onerror="try { window.parent.postMessage({type:'adsterra_blocked', key:'${zoneKey}'}, '*'); } catch(e){}"
          ></script>
        </body>
      </html>
    `;

    containerRef.current.innerHTML = '';
    containerRef.current.appendChild(iframe);

    try {
      const doc = iframe.contentWindow || iframe.contentDocument;
      if (doc && doc.document) {
        doc.document.open();
        doc.document.write(html);
        doc.document.close();
      } else if (doc) {
        doc.open();
        doc.write(html);
        doc.close();
      }
    } catch (e) {
      iframe.srcdoc = html;
    }

    // Verificación de respaldo: si tras 3s no hay contenido renderizado en el iframe
    const fallbackTimer = setTimeout(() => {
      try {
        const idoc = iframe.contentDocument || iframe.contentWindow?.document;
        if (idoc && idoc.body && idoc.body.innerHTML.trim() === '') {
          if (onBlocked) onBlocked();
        }
      } catch (e) {
        // Si hay cross-origin, significa que el iframe cargó un ad externo con éxito
      }
    }, 3000);

    return () => {
      window.removeEventListener('message', handleMsg);
      clearTimeout(fallbackTimer);
      if (containerRef.current) {
        containerRef.current.innerHTML = '';
      }
    };
  }, [zoneKey, width, height, onBlocked]);

  return (
    <div 
      ref={containerRef} 
      className={`adsterra-banner-slot ${className}`}
      style={{
        width: '100%',
        maxWidth: `${width}px`,
        minHeight: `${height}px`,
        margin: '0 auto',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        overflow: 'hidden'
      }}
    />
  );
}
