#!/bin/bash
# deploy.sh - Despliegue rápido con Docker Compose

set -e

echo "🚀 Iniciando despliegue del pipeline de noticias..."
echo "=================================================="

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose no está instalado"
    exit 1
fi

echo "✅ Docker y Docker Compose detectados"

# Verificar .env
if [ ! -f .env ]; then
    echo "⚠️  Archivo .env no encontrado, creando uno de ejemplo..."
    echo "GEMINI_API_KEY=TU_API_KEY_AQUI" > .env
    echo "   Por favor edita .env con tu API Key de Gemini"
fi

# Crear directorios
echo "📁 Creando directorios..."
mkdir -p data/{raw,clean,analysis,economic,results,commoncrawl}

# Construir y desplegar
echo "🔨 Construyendo imágenes..."
docker-compose build

echo "🛑 Deteniendo contenedores anteriores..."
docker-compose down

echo "🚀 Iniciando servicios..."
docker-compose up -d

sleep 5

echo ""
echo "📊 Estado de los contenedores:"
docker-compose ps

echo ""
echo "=================================================="
echo "✅ Despliegue completado!"
echo ""
echo "📊 Dashboard: http://localhost:8080"
echo ""
echo "Comandos útiles:"
echo "  Ver logs:     docker-compose logs -f"
echo "  Detener:      docker-compose down"
echo "  Estado:       docker-compose ps"