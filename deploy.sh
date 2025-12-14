#!/bin/bash



set -e  # Salir si hay algún error

echo "🚀 Iniciando despliegue del pipeline de noticias..."
echo "=================================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar que Docker está instalado
if ! command -v docker &> /dev/null; then
    print_error "Docker no está instalado. Por favor instala Docker primero."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose no está instalado. Por favor instala Docker Compose primero."
    exit 1
fi

print_info "Docker y Docker Compose detectados ✓"

# Crear directorios de datos si no existen
print_info "Creando estructura de directorios..."
mkdir -p data/{raw,clean,analysis,economic,results}
print_info "Directorios creados ✓"

# Construir imágenes Docker
print_info "Construyendo imágenes Docker..."
docker-compose build

if [ $? -eq 0 ]; then
    print_info "Imágenes construidas exitosamente ✓"
else
    print_error "Error al construir las imágenes"
    exit 1
fi

# Detener contenedores existentes
print_info "Deteniendo contenedores existentes (si los hay)..."
docker-compose down

# Iniciar servicios
print_info "Iniciando servicios..."
docker-compose up -d

if [ $? -eq 0 ]; then
    print_info "Servicios iniciados exitosamente ✓"
else
    print_error "Error al iniciar los servicios"
    exit 1
fi

# Esperar unos segundos para que los servicios se inicien
sleep 5

# Verificar estado de los contenedores
print_info "Verificando estado de los contenedores..."
echo ""
docker-compose ps
echo ""

# Verificar que el dashboard esté accesible
print_info "Verificando acceso al dashboard..."
sleep 3

if curl -s http://localhost:8080 > /dev/null; then
    print_info "Dashboard accesible en http://localhost:8080 ✓"
else
    print_warning "El dashboard podría no estar listo aún. Espera unos segundos más."
fi

# Mostrar logs de los últimos 20 líneas
print_info "Mostrando logs recientes..."
echo ""
docker-compose logs --tail=20

echo ""
echo "=================================================="
print_info "✅ Despliegue completado!"
echo ""
echo "Servicios disponibles:"
echo "  📊 Dashboard: http://localhost:8080"
echo ""
echo "Comandos útiles:"
echo "  Ver logs:        docker-compose logs -f [servicio]"
echo "  Detener:         docker-compose down"
echo "  Reiniciar:       docker-compose restart [servicio]"
echo "  Ver estado:      docker-compose ps"
echo ""
print_info "Pipeline ejecutándose en segundo plano"