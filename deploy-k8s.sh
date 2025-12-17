#!/bin/bash
# deploy-k8s.sh - Despliegue completo en Kubernetes

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     🚀 DESPLIEGUE EN KUBERNETES - Pipeline de Noticias     ║"
echo "╚════════════════════════════════════════════════════════════╝"

# Verificar kubectl
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl no está instalado"
    exit 1
fi

# Verificar conexión
echo "📡 Verificando conexión al cluster..."
kubectl cluster-info > /dev/null 2>&1 || {
    echo "❌ No hay conexión al cluster. Ejecuta: minikube start"
    exit 1
}
echo "✅ Conectado al cluster"

# Construir imágenes
echo ""
echo "🔨 Construyendo imágenes Docker..."
docker-compose build

# Cargar imágenes en Minikube (si aplica)
if command -v minikube &> /dev/null; then
    echo ""
    echo "📦 Cargando imágenes en Minikube..."
    for img in downloader processor analyzer economic_data correlator dashboard commoncrawl; do
        echo "   Cargando proyecto_${img}..."
        minikube image load "proyecto_${img}:latest" 2>/dev/null || true
    done
fi

# Crear recursos
echo ""
echo "📁 Creando namespace..."
kubectl apply -f k8s/namespace.yml

echo ""
echo "🔐 Creando secret de Gemini..."
kubectl apply -f k8s/secret-gemini.yml

echo ""
echo "💾 Creando almacenamiento..."
kubectl apply -f k8s/pvc.yml

echo ""
echo "🚀 Desplegando servicios..."
kubectl apply -f k8s/deployment-downloader.yml
kubectl apply -f k8s/deployment-commoncrawl.yml
kubectl apply -f k8s/deployment-processor.yml
kubectl apply -f k8s/deployment-analyzer.yml
kubectl apply -f k8s/deployment-economic.yml
kubectl apply -f k8s/deployment-correlator.yml
kubectl apply -f k8s/deployment-dashboard.yml
kubectl apply -f k8s/services.yml

# Esperar
echo ""
echo "⏳ Esperando que los pods estén listos..."
sleep 10

# Estado
echo ""
echo "════════════════════════════════════════════════════════════"
echo "📊 ESTADO DEL DESPLIEGUE:"
echo "════════════════════════════════════════════════════════════"
kubectl get pods -n news-pipeline
echo ""
kubectl get svc -n news-pipeline

echo ""
echo "════════════════════════════════════════════════════════════"
echo "✅ DESPLIEGUE COMPLETADO"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "📊 Para acceder al Dashboard:"
echo "   kubectl port-forward svc/dashboard-svc 8080:8080 -n news-pipeline"
echo "   Luego abre: http://localhost:8080"
echo ""
echo "📝 Comandos útiles:"
echo "   Ver pods:     kubectl get pods -n news-pipeline"
echo "   Ver logs:     kubectl logs -f <pod> -n news-pipeline"
echo "   Eliminar:     kubectl delete namespace news-pipeline"