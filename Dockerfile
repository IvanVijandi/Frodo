# syntax=docker/dockerfile:1
FROM python:3.10-slim

##Creamos el directorio de trabajo en el contenedor
WORKDIR /app

# Instalar dependencias del sistema necesarias para algunas librerías de Python (como PyMuPDF o grpc)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requeriments.txt .

# Usamos el cache de BuildKit para no descargar paquetes en cada rebuild
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requeriments.txt

#Copiamos toda la app en el directorio /app del contenedor
COPY . /app

EXPOSE 8000

CMD ["uvicorn", "FastApi.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
