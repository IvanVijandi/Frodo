## Why

Actualmente, el backend (FastAPI y Langchain) se ejecuta localmente fuera de los contenedores de Docker, mientras que servicios críticos como Milvus y Ollama sí están orquestados con Docker Compose. Contenerizar el backend resuelve problemas de dependencias locales, asegura la reproducibilidad en distintos entornos de despliegue y permite que el backend se comunique de manera nativa y directa mediante la red interna de Docker con Milvus y Ollama.

## What Changes

- Se añadirá un `Dockerfile` en la raíz del proyecto configurado para ejecutar el servidor FastAPI.
- Se actualizará el archivo `docker-compose.yml` para incluir un nuevo servicio `backend` que construya la imagen desde el `Dockerfile`.
- Se configurarán las variables de entorno dentro del `docker-compose.yml` para que el backend se conecte a Milvus y Ollama usando los nombres de host internos de Docker (ej. `milvus-standalone` y `ollama`).

## Capabilities

### New Capabilities
- `docker-deployment`: Capacidad de orquestar el entorno completo (backend, base de datos y modelos) utilizando un único archivo `docker-compose.yml` y `Dockerfile`.

### Modified Capabilities


## Impact

- **APIs**: El endpoint de la API seguirá siendo expuesto en el puerto 8000 (mapeado desde el contenedor hacia la máquina host).
- **Dependencies**: Se requerirá mantener el archivo `requeriments.txt` actualizado para que el contenedor instale correctamente las dependencias en la fase de `build`.
- **Systems**: El `docker-compose.yml` se convertirá en la fuente única de verdad para levantar el ecosistema completo de MARIA.
