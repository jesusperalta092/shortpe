# DramaPe (ShortPe) 🎬

Plataforma de streaming de doramas cortos estilo Netflix, optimizada para alta concurrencia, experiencia móvil/tablet premium y despliegue automatizado en Railway.

---

## 🚀 Características Principales

- **Diseño Netflix Moderno y Responsivo**: Experiencia de usuario inmersiva optimizada para móvil, tablet y escritorio.
- **Proxy Streaming de Alto Rendimiento**: Servidor backend en Python con soporte para HLS (`.m3u8`), MP4 directo, streaming con Range bytes y caché inteligente en disco.
- **Bypass SSL y Tokens Dinámicos**: Resolución en vivo de firmas AWS S3 para CDNs externas sin caídas 502 ni bloqueos CORS.
- **SEO & GEO Optimizado**: Metadatos OpenGraph, Twitter Cards, JSON-LD (`WebSite`, `Organization`, `TVSeries`) y etiquetas geográficas para Perú (`es-PE`) y Latinoamérica.
- **Listo para Producción**: Configurado con Docker, Docker Compose y `railway.json` para despliegue con 1-clic en Railway.

---

## 🛠️ Stack Tecnológico

- **Frontend**: Next.js 15, React 19, Lucide Icons, Hls.js
- **Backend / Proxy**: Python 3.11+, Requests, Urllib3
- **Contenedor**: Docker multi-stage (Node.js + Python)
- **Deployment**: Railway / VPS

---

## 📦 Instalación y Ejecución Local

### 1. Clonar el repositorio
```bash
git clone https://github.com/jesusperalta092/shortpe.git
cd shortpe
```

### 2. Instalar dependencias
```bash
# Dependencias de Python
pip install -r requirements.txt

# Dependencias de Next.js
cd web-next
npm install
cd ..
```

### 3. Iniciar el proyecto
```bash
# Iniciar servidor proxy Python (puerto 8090)
python server.py

# En otra terminal, iniciar Next.js frontend (puerto 3000)
cd web-next
npm run dev
```

Abre `http://localhost:3000` en tu navegador.

---

## 🚢 Despliegue en Railway

El proyecto incluye `Dockerfile`, `start.sh` y `railway.json`. Para desplegar:
1. Conecta este repositorio en tu dashboard de Railway.
2. Railway detectará automáticamente el `Dockerfile` y levantará tanto el backend proxy como el frontend Next.js en un solo contenedor optimizado.

---

## 📄 Licencia

MIT License.
