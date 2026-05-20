## Why

Este cambio es necesario para permitir a los usuarios subir documentos PDF al sistema. Al procesar estos documentos, dividirlos (splitting) y almacenar sus embeddings en Milvus, habilitamos y nutrimos las capacidades de recuperación de información (RAG) sobre el conocimiento proporcionado por el usuario.

## What Changes

- Se añadirá un nuevo endpoint en FastAPI (`/upload-file`) que acepte la carga de archivos PDF.
- Se implementará un mecanismo de extracción de texto del documento y división (text splitting).
- Se generarán embeddings a partir de los fragmentos de texto resultantes.
- Se insertarán los embeddings generados, junto con sus metadatos correspondientes, en la base de datos vectorial Milvus.

## Capabilities

### New Capabilities

- `pdf-upload-processing`: Capacidad de recibir un archivo PDF a través de la API, extraer su texto, dividirlo en fragmentos (chunks), generar los embeddings usando un modelo de lenguaje y almacenarlos en la base de datos vectorial Milvus.

### Modified Capabilities


## Impact

- **APIs**: Creación del nuevo endpoint `/upload-file` en el servicio FastAPI.
- **Dependencies**: Posible necesidad de librerías adicionales para la lectura y procesamiento de archivos PDF (por ejemplo, `PyMuPDF` o `pypdf`), así como el uso de Langchain/Ollama para la generación de los embeddings.
- **Systems**: Interacción con Milvus para la inserción de datos vectoriales (colecciones e índices).
