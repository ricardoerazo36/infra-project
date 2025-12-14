FROM python:3.10-slim

WORKDIR /app

# Dependencias del sistema que newspaper3k necesita
RUN apt-get update && apt-get install -y \
    libxml2 \
    libxslt1.1 \
    libxslt1-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
