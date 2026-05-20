## ADDED Requirements

### Requirement: Backend Docker Image
El sistema SHALL proveer un archivo `Dockerfile` capaz de empaquetar la aplicación FastAPI junto con sus dependencias.

#### Scenario: Construcción exitosa de la imagen
- **WHEN** se ejecuta el comando `docker build` (o mediante docker-compose up --build).
- **THEN** la imagen se compila sin errores, instalando todos los paquetes requeridos de `requeriments.txt` e indicando el comando de inicio (`uvicorn`).

### Requirement: Docker Compose Integration
El sistema SHALL incluir el backend como un nuevo servicio dentro de `docker-compose.yml`, conectado a la misma red que Milvus y Ollama.

#### Scenario: Intercomunicación de contenedores
- **WHEN** el backend recibe una petición e intenta conectar a Milvus u Ollama.
- **THEN** el backend logra resolver exitosamente los hostnames `milvus-standalone` y `ollama`, procesando la petición correctamente gracias a las variables de entorno inyectadas.
