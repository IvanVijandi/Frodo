# syntax=docker/dockerfile:1
FROM python:3.10-slim

##Creamos el directorio de trabajo en el contenedor
WORKDIR /app

# Instalar dependencias del sistema necesarias para algunas librerías de Python (como PyMuPDF o grpc)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar uv desde su imagen oficial para usarlo como instalador de paquetes ultrarrápido
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock ./

# Forzamos a uv a crear el entorno virtual fuera de /app para que el volumen de Docker no lo oculte
ENV UV_PROJECT_ENVIRONMENT="/opt/venv"
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH="/app"

# Sincronizamos las dependencias usando el lockfile
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Copiamos toda la app en el directorio /app del contenedor
COPY . /app

EXPOSE 8000

CMD ["uvicorn", "FastApi.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
