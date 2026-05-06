## Why
Se necesita una interfaz gráfica para administrar, visualizar y explorar los datos y la configuración de la base de datos vectorial Milvus, la cual ya está configurada o se planea configurar. Attu es la herramienta oficial de gestión para Milvus que facilita enormemente esta tarea, permitiendo ver las colecciones y entidades directamente.

## What Changes
- Agregar un nuevo servicio `attu` al archivo `docker-compose.yml` existente.
- Configurar el servicio para que se conecte a la instancia de Milvus.
- Exponer el puerto adecuado para acceder a la interfaz web de Attu (típicamente 8000).

## Capabilities

### New Capabilities
- `attu-ui`: Interfaz gráfica web para la administración y visualización de la base de datos vectorial Milvus a través de Docker.

### Modified Capabilities

## Impact
- Archivo modificado: `docker-compose.yml`.
- Se requiere exponer un nuevo puerto para el host (por defecto 8000).
- No hay impacto en el código de la aplicación.
