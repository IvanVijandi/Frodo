## Why

Actualmente, la lógica de procesamiento de PDFs se encuentra encapsulada dentro del `pdf_service.py`, lo que dificulta la visibilidad, depuración y la gestión del flujo secuencial directamente desde la capa de la API (FastAPI). Además, la configuración actual no hace uso adecuado de un sistema centralizado de variables de entorno y configuraciones (`env` y `config`), lo que limita la flexibilidad para alternar fácilmente entre modelos locales y APIs de terceros (para LLM, Reranker o Embeddings). Mover la lógica secuencial al endpoint y estandarizar la configuración permitirá un código más limpio, mantenible y adaptable.

## What Changes

- Mover la lógica principal de procesamiento de PDFs desde `pdf_service.py` hacia el endpoint de FastAPI.
- Invocar secuencialmente en el endpoint las instancias necesarias: el cliente de Milvus, el generador de embeddings, el text splitter y cualquier otro componente implicado.
- Refactorizar la forma en que se manejan las variables de configuración, incorporando el uso de un archivo `.env` y/o un módulo de `config` para gestionar dinámicamente qué modelos (locales o API) se deben utilizar para LLM, Embeddings y Reranker.
- Actualizar dependencias y referencias que dependan de `pdf_service.py` para asegurar que todo el flujo en el endpoint funcione sin problemas.

## Capabilities

### New Capabilities
- `pdf-sequential-endpoint`: Refactorización del endpoint de subida de PDF para ejecutar los pasos de manera secuencial (extracción, split, embedding y guardado en Milvus) utilizando componentes individuales.
- `dynamic-model-config`: Nuevo sistema de configuración basado en `.env` y archivos `config` para cargar dinámicamente modelos locales o APIs para LLMs, Rerankers y Embeddings.

### Modified Capabilities
- `pdf-upload-processing`: Se modifica la forma en la que se orquesta el procesamiento del PDF, que pasará a estar controlado por el router de FastAPI en lugar de un servicio monolítico.

## Impact

- **Código Afectado**: `pdf_service.py` (posible eliminación o reducción significativa a utilidades menores), routers/endpoints de FastAPI relacionados a PDFs.
- **Configuraciones**: Introducción o modificación del archivo `.env` y el módulo de configuración de la app para gestionar modelos de LLM, embeddings y rerankers.
- **Dependencias y Componentes**: Interacción más directa desde el endpoint con clientes de Milvus, Langchain (splitters, embeddings).
