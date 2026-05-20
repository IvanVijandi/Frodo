FROM python:3.10-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias para algunas librerías de Python (como PyMuPDF o grpc)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requeriments.txt .

RUN pip install --no-cache-dir -r requeriments.txt

# Como en desarrollo montaremos el volumen, esto es solo para cuando se construya sin volumen
COPY . /app

EXPOSE 8000

CMD ["uvicorn", "FastApi.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
