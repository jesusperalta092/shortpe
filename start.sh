#!/bin/sh
set -e

echo "=== Iniciando DramaPe (Producción) ==="

# 1. Arrancar el Backend Python de streaming/catálogo en segundo plano (puerto 8090)
echo "[1/2] Iniciando Backend Python (server.py en :8090)..."
python3 server.py &
BACKEND_PID=$!

# Esperar a que el backend esté listo
sleep 2

# 2. Arrancar el Frontend Next.js en el puerto asignado por Railway ($PORT o 3000)
APP_PORT=${PORT:-3000}
echo "[2/2] Iniciando Frontend Next.js en puerto :$APP_PORT..."

# Función para apagar ambos procesos al recibir señal de término
cleanup() {
  echo "Apagando servicios..."
  kill -TERM "$BACKEND_PID" 2>/dev/null || true
  exit 0
}
trap cleanup SIGINT SIGTERM

cd web-next
exec node_modules/.bin/next start -p "$APP_PORT"
