# =========================================================
# Dockerfile para DramaPe (Railway / Producción)
# =========================================================
FROM node:20-bookworm-slim

# Instalar Python 3 y utilidades requeridas
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-requests \
    python3-urllib3 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1. Copiar dependencias de Python y Node.js para cachear capas
COPY requirements.txt ./
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt || true

COPY web-next/package*.json ./web-next/
RUN cd web-next && npm ci --legacy-peer-deps

# 2. Copiar todo el código fuente del proyecto
COPY . .

# 3. Compilar el frontend Next.js para producción
RUN cd web-next && npm run build

# 4. Asegurar permisos de ejecución para el script de inicio
RUN chmod +x start.sh

# Puerto por defecto (Railway inyecta su propio $PORT en tiempo de ejecución)
EXPOSE 3000

ENV NODE_ENV=production
ENV PORT=3000

CMD ["./start.sh"]
