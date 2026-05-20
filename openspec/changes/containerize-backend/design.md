## Context

El proyecto MARIA-1 consta de una API construida con FastAPI que se apoya en modelos de IA (Langchain, Ollama) y bases de datos vectoriales (Milvus). Hasta el momento, el backend se ha ejecutado de manera nativa en el entorno de desarrollo, lo que requiere instalar dependencias locales manualmente y gestionar la red para alcanzar a Milvus y Ollama, que sí corren en contenedores locales. 
Para consolidar la infraestructura, necesitamos que el backend de FastAPI sea también un servicio dockerizado dentro de la misma red (`maria-1_default` o una red dedicada).

## Goals / Non-Goals

**Goals:**
- Construir un `Dockerfile` optimizado para Python/FastAPI que instale los requerimientos y exponga el puerto 8000.
- Integrar este contenedor dentro del `docker-compose.yml` existente como el servicio `backend`.
- Ajustar las variables de entorno para usar la resolución DNS interna de Docker (apuntando a `milvus-standalone` en lugar de `localhost`).

**Non-Goals:**
- Configuración de orquestadores avanzados como Kubernetes o despliegues multi-nodo (Swarm).
- Despliegue en la nube (AWS/GCP/Azure) en esta iteración.
- Cambios arquitectónicos en el código de FastAPI, salvo por el manejo de las variables de entorno.

## Decisions

1. **Imagen base del Dockerfile**: `python:3.10-slim` (o la versión que se esté utilizando).
   - *Rationale*: Las imágenes "slim" son mucho más ligeras que las completas, pero contienen lo suficiente para compilar paquetes típicos de Python. Es la práctica estándar para microservicios.
2. **Volúmenes vs Copia estática**: En el `docker-compose.yml`, se montará el directorio actual como un volumen (`.:/app`) en el servicio del backend.
   - *Rationale*: Dado que estamos en fase de desarrollo, montar el código permite aprovechar el `--reload` de uvicorn sin tener que reconstruir la imagen de Docker en cada cambio.
3. **Variables de Entorno**: Configuración directa en el `docker-compose.yml` usando la sección `environment` o a través de un archivo `.env`.
   - *Rationale*: Se inyectará `MILVUS_URI=http://milvus-standalone:19530` y `OLLAMA_URI=http://ollama:11434` al contenedor, reemplazando a `localhost`.

## Risks / Trade-offs

- **[Riesgo] Resolución DNS en Docker**: A veces la red default no resuelve correctamente si los servicios no dependen unos de otros o arrancan antes de tiempo.
  - *Mitigación*: Se configurará explícitamente la directiva `depends_on` en el servicio `backend` apuntando a `milvus-standalone` y `ollama` para asegurar un orden de arranque correcto.
