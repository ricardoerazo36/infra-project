# 📰 Pipeline de Análisis de Noticias y Correlación con COLCAP

## 👥 Integrantes del Grupo

| Nombre | Código | Correo |
|--------|--------|--------|
| Ricardo Erazo Muñoz | 2242117 | ricardo.erazo@correounivalle.edu.co |
| Heidy Gelpud | 2242550 | heidy.gelpud@correounivalle.edu.co |
| James Calero | 2243461 | james.calero@correounivalle.edu.co |

---

## 📋 Descripción del Proyecto

Este proyecto implementa un **pipeline de datos completo** que recolecta noticias de Colombia, las procesa, analiza y correlaciona con el comportamiento del índice bursátil **COLCAP** de la Bolsa de Valores de Colombia.

### ¿Qué hace el sistema?

Imagina que tienes un equipo de analistas trabajando 24/7:

1. **📥 Descargador**: Como un lector que revisa periódicos constantemente, descarga noticias de fuentes RSS colombianas (El Tiempo, Portafolio, El Espectador).

2. **🔄 Procesador**: Limpia y organiza las noticias, como un editor que quita el "ruido" (HTML, caracteres raros) y deja solo el contenido importante.

3. **📊 Analizador**: Clasifica cada noticia por tema (economía, seguridad, política, salud), como un archivista que organiza documentos por categorías.

4. **💹 Recolector Económico**: Obtiene el valor actual del COLCAP usando la API de Gemini (IA de Google), como un analista financiero consultando la bolsa.

5. **🔗 Correlador**: El "cerebro" del sistema - busca patrones entre las noticias y el mercado. ¿Más noticias de seguridad = cambio en el COLCAP?

6. **📈 Dashboard**: Una interfaz web donde puedes ver todos los resultados de forma visual.

7. **🌐 Common Crawl**: Fuente adicional que obtiene noticias históricas de archivos web masivos.

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                        FUENTES DE DATOS                          │
├─────────────────────────────────────────────────────────────────┤
│  📡 RSS Feeds          🌐 Common Crawl         💹 Gemini API    │
│  (El Tiempo, etc.)     (Archivo histórico)     (Datos COLCAP)   │
└────────┬───────────────────────┬─────────────────────┬──────────┘
         │                       │                     │
         ▼                       ▼                     ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   DOWNLOADER    │    │  COMMONCRAWL    │    │  ECONOMIC_DATA  │
│   (RSS Parser)  │    │   (Fetcher)     │    │   (Collector)   │
└────────┬────────┘    └────────┬────────┘    └────────┬────────┘
         │                      │                      │
         ▼                      ▼                      │
┌─────────────────────────────────────────┐           │
│              data/raw/                   │           │
│         (Noticias sin procesar)          │           │
└────────────────┬────────────────────────┘           │
                 │                                     │
                 ▼                                     │
┌─────────────────────────────────────────┐           │
│             PROCESSOR                    │           │
│      (Limpieza y normalización)          │           │
└────────────────┬────────────────────────┘           │
                 │                                     │
                 ▼                                     │
┌─────────────────────────────────────────┐           │
│             data/clean/                  │           │
│         (Noticias procesadas)            │           │
└────────────────┬────────────────────────┘           │
                 │                                     │
                 ▼                                     │
┌─────────────────────────────────────────┐           │
│              ANALYZER                    │           │
│     (Clasificación por categorías)       │           │
└────────────────┬────────────────────────┘           │
                 │                                     │
                 ▼                                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                         CORRELATOR                               │
│            (Análisis estadístico de correlaciones)               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                          DASHBOARD                               │
│                    (Visualización Web)                           │
│                    http://localhost:8080                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tecnologías Utilizadas

| Componente | Tecnología | Propósito |
|------------|------------|-----------|
| Backend | Python 3.10 | Lógica de procesamiento |
| Contenedores | Docker & Docker Compose | Orquestación de servicios |
| Orquestación K8s | Kubernetes (Minikube) | Despliegue escalable |
| API IA | Google Gemini | Obtención de datos financieros |
| Dashboard | Flask + Chart.js | Visualización web |
| Análisis | NumPy, Pandas | Cálculos estadísticos |

---

## 📁 Estructura del Proyecto

```
proyecto/
├── 📄 docker-compose.yml      # Orquestación de contenedores
├── 📄 deploy.sh               # Script de despliegue Docker
├── 📄 deploy-k8s.sh           # Script de despliegue Kubernetes
├── 📄 .env                    # Variables de entorno (API Keys)
│
├── 📁 downloader/             # Servicio de descarga RSS
│   ├── main_loop.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── 📁 processor/              # Servicio de procesamiento
│   ├── main_loop.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── 📁 analyzer/               # Servicio de análisis temático
│   ├── main_loop.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── 📁 economic_data/          # Recolector de datos económicos
│   ├── main_loop.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── 📁 correlator/             # Servicio de correlación
│   ├── main_loop.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── 📁 dashboard/              # Interfaz web
│   ├── app.py
│   ├── templates/
│   │   └── index.html
│   ├── Dockerfile
│   └── requirements.txt
│
├── 📁 commoncrawl/            # Fetcher de Common Crawl
│   ├── main_loop.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── 📁 k8s/                    # Manifiestos de Kubernetes
│   ├── namespace.yml
│   ├── pvc.yml
│   ├── secret-gemini.yml
│   ├── deployment-*.yml
│   └── services.yml
│
└── 📁 data/                   # Datos generados (volumen)
    ├── raw/                   # Noticias descargadas
    ├── clean/                 # Noticias procesadas
    ├── analysis/              # Conteos por categoría
    ├── economic/              # Datos del COLCAP
    ├── results/               # Correlaciones calculadas
    └── commoncrawl/           # Datos de Common Crawl
```

---

## 🚀 Instrucciones de Instalación y Ejecución

### Prerrequisitos

Antes de comenzar, asegúrate de tener instalado:

- **Docker** (versión 20.10 o superior)
- **Docker Compose** (versión 2.0 o superior)
- **Git** (para clonar el repositorio)

Para verificar las instalaciones:

```bash
docker --version
docker-compose --version
git --version
```

### Opción 1: Despliegue con Docker Compose

Esta es la forma más sencilla de ejecutar el proyecto.

#### Paso 1: Clonar el repositorio

```bash
git clone https://github.com/ricardoerazo36/infra-project.git
```

#### Paso 2: Configurar la API Key de Gemini

El proyecto usa la API de Google Gemini para obtener datos del COLCAP. Ya viene configurada una API Key de prueba.

#### Paso 3: Ejecutar el despliegue

```bash
# Dar permisos de ejecución al script
chmod +x deploy.sh

# Ejecutar el despliegue
./deploy.sh
```

O manualmente:

```bash
# Crear directorios de datos
mkdir -p data/{raw,clean,analysis,economic,results,commoncrawl}

# Construir las imágenes
docker-compose build

# Iniciar todos los servicios
docker-compose up -d
```

#### Paso 4: Verificar que todo esté funcionando

```bash
# Ver el estado de los contenedores
docker-compose ps

# Ver los logs en tiempo real
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f downloader
```

#### Paso 5: Acceder al Dashboard

Abre tu navegador y visita:

```
http://localhost:8080
```

🎉 ¡Listo! El sistema comenzará a recolectar noticias automáticamente.

---

### Opción 2: Despliegue con Kubernetes (Minikube)

Para un despliegue más robusto y escalable.

#### Prerrequisitos adicionales

```bash
# Instalar Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Instalar kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install kubectl /usr/local/bin/kubectl
```

#### Paso 1: Iniciar Minikube

```bash
# Iniciar el cluster
minikube start --driver=docker --memory=4096 --cpus=2

# Verificar que esté funcionando
kubectl cluster-info
```

#### Paso 2: Ejecutar el despliegue

```bash
# Dar permisos de ejecución
chmod +x deploy-k8s.sh

# Ejecutar el despliegue en Kubernetes
./deploy-k8s.sh
```

#### Paso 3: Acceder al Dashboard

```bash
# Crear un túnel para acceder al dashboard
kubectl port-forward svc/dashboard-svc 8080:8080 -n news-pipeline

# Abrir en el navegador
# http://localhost:8080
```

#### Comandos útiles de Kubernetes

```bash
# Ver todos los pods
kubectl get pods -n news-pipeline

# Ver logs de un pod
kubectl logs -f <nombre-del-pod> -n news-pipeline

# Ver servicios
kubectl get svc -n news-pipeline

# Escalar un deployment
kubectl scale deployment news-processor --replicas=3 -n news-pipeline

# Eliminar todo el despliegue
kubectl delete namespace news-pipeline
```

---

## 📊 Uso del Dashboard

Una vez que el sistema esté funcionando, el Dashboard te mostrará:

### Panel Principal

1. **Estado del Sistema**: Indica si todos los servicios están operativos.

2. **Correlaciones Detectadas**: Muestra la relación entre cada categoría de noticias y el COLCAP:
   - 🟢 **Verde (positiva)**: Más noticias de este tema = COLCAP sube
   - 🔴 **Rojo (negativa)**: Más noticias de este tema = COLCAP baja
   - 🟡 **Amarillo (neutral)**: No hay correlación clara

3. **Insights**: Interpretaciones automáticas de los datos.

4. **Gráfico de Evolución**: Muestra la cantidad de noticias por tema a lo largo del tiempo.

## ⚙️ Configuración y Personalización

### Variables de Entorno

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `GEMINI_API_KEY` | API Key de Google Gemini | (requerida) |
| `SLEEP_INTERVAL` | Intervalo entre ejecuciones (segundos) | Varía por servicio |

### Intervalos por Servicio

| Servicio | Intervalo | Descripción |
|----------|-----------|-------------|
| Downloader | 1 hora | Descarga nuevas noticias |
| Processor | 30 min | Procesa noticias pendientes |
| Analyzer | 30 min | Analiza y clasifica |
| Economic Data | 1 hora | Actualiza COLCAP |
| Correlator | 1 hora | Calcula correlaciones |
| Common Crawl | 24 horas | Busca en archivo histórico |

## 🔧 Comandos Útiles

### Docker Compose

```bash
# Iniciar todos los servicios
docker-compose up -d

# Detener todos los servicios
docker-compose down

# Ver logs de todos los servicios
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f analyzer

# Reiniciar un servicio
docker-compose restart correlator

# Reconstruir y reiniciar
docker-compose up -d --build

# Ver uso de recursos
docker stats
```

### Inspeccionar Datos

```bash
# Ver noticias descargadas
ls -la data/raw/

# Ver noticias procesadas
ls -la data/clean/

# Ver análisis por día
cat data/analysis/daily_counts.json

# Ver datos del COLCAP
cat data/economic/colcap_historical.json

# Ver correlaciones
cat data/results/correlations_latest.json
```

---

## 🐛 Solución de Problemas

### El Dashboard no carga datos

**Síntoma**: El dashboard muestra "Sistema iniciándose..."

**Solución**: 
1. Espera unos minutos, el sistema necesita tiempo para recolectar datos.
2. Verifica que los servicios estén corriendo:
   ```bash
   docker-compose ps
   ```

### Error de conexión con Gemini

**Síntoma**: Logs muestran "Error de conexión con Gemini"

**Solución**:
1. Verifica tu API Key en `.env`
2. Verifica tu conexión a internet
3. El sistema usará valores de respaldo automáticamente

### Contenedor se reinicia constantemente

**Síntoma**: Un contenedor aparece en estado "Restarting"

**Solución**:
```bash
# Ver logs del contenedor problemático
docker-compose logs <nombre_servicio>

# Reiniciar el servicio
docker-compose restart <nombre_servicio>
```

### Espacio en disco

**Síntoma**: El sistema deja de funcionar por falta de espacio

**Solución**:
```bash
# Limpiar datos antiguos
rm -rf data/raw/*.json
rm -rf data/clean/*.json

# Limpiar imágenes Docker no usadas
docker system prune -a
```

---

## 📈 Métricas y Monitoreo

### Ver Estadísticas del Sistema

```bash
# Uso de CPU y memoria por contenedor
docker stats

# Cantidad de archivos procesados
find data/clean -name "*.json" | wc -l

# Ver las últimas correlaciones
cat data/results/correlations_latest.json | python -m json.tool
```
</div>
