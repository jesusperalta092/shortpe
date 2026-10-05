# 📺 DramaTube - Módulo de Integración

Este espacio está 100% aislado y modularizado para gestionar la sección **DramaTube**.

---

## 📁 Estructura del Módulo

* **`modules/dramatube.py`**: Motor principal. Contiene la lógica de desencriptación AES-GCM, consulta a APIs de upstream y parseo de metadata y subtítulos.
* **`extractors/dramatube/scraper.py`**: Script ejecutable para añadir nuevas series a DramaTube o re-escanear las existentes.
* **`extractors/dramatube/test_suite.py`**: Suite de validación para verificar que todos los enlaces `.m3u8` y subtítulos `.srt`/`.vtt` de DramaTube estén activos.
* **`data/dramatube.json`**: Base de datos JSON independiente y dedicada exclusivamente a DramaTube.

---

## 🚀 Cómo agregar una nueva serie a DramaTube

1. Abre `extractors/dramatube/scraper.py`.
2. Añade el slug de la serie en la lista `VERIFIED_SLUGS` (ejemplo: `'nombre-del-drama'`).
3. Ejecuta:
   ```bash
   python extractors/dramatube/scraper.py
   ```
4. Para validar que todo funciona:
   ```bash
   python extractors/dramatube/test_suite.py
   ```

---

## ⚡ Ventajas de esta arquitectura modular
1. **Aislamiento Total**: Modificar DramaTube no afecta a HotDrama, DramaVibe ni a otras secciones.
2. **Fácil Mantenimiento**: Encuentra errores y logs de extracción en un solo lugar.
3. **Escalable**: Puedes agregar decenas de títulos con un solo comando.
