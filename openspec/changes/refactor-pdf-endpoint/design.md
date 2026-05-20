## Context

Actualmente, el flujo de ingesta de archivos PDF se gestiona mediante un servicio monolítico (`pdf_service.py`), el cual oculta la lógica de orquestación de la API (FastAPI) y dificulta el manejo de errores, la observabilidad y el control secuencial de los pasos: validación, extracción de texto, división del texto (splitting), generación de embeddings, y almacenamiento en Milvus. Además, no existe un mecanismo centralizado dinámico basado en un `.env` y archivo de configuración para seleccionar si se utilizan modelos locales u hospedados (API) para LLM, Embeddings y Reranker, lo que vuelve rígido el código actual.

## Goals / Non-Goals

**Goals:**
- Mover la orquestación del procesamiento de PDFs (extracción, chunking, embeddings, Milvus) al propio endpoint de FastAPI, llamando a cada componente secuencialmente.
- Implementar un sistema de configuración con `.env` que permita cargar dinámicamente el proveedor y tipo de modelo para LLMs, Rerankers y Embeddings (ej: local vs externo).
- Deprecar/simplificar `pdf_service.py`, moviendo la instanciación de dependencias (Langchain, Milvus client) al contexto del router/inyección de dependencias de FastAPI.

**Non-Goals:**
- Cambiar la base de datos vectorial (se mantiene Milvus).
- Implementar nuevos métodos de extracción de texto avanzado (se mantienen las librerías actuales pero reorganizadas).
- Reestructurar otros endpoints que no estén relacionados con la carga y procesamiento de PDFs.

## Decisions

- **Orquestación en el Endpoint**: Se elimina el "black-box" de `pdf_service`. En el endpoint de FastAPI, inyectaremos las dependencias (ej. `MilvusClient`, `EmbeddingGenerator`, `TextSplitter`) y ejecutaremos los pasos secuencialmente. Esto nos permitirá controlar el ciclo de vida de la request y retornar un mejor feedback/status al cliente si algún paso falla.
- **Gestión de Configuración**: Se creará un módulo de configuración robusto (posiblemente usando `pydantic-settings`) que lea de un `.env`. Este módulo expondrá variables como `EMBEDDING_PROVIDER` (ej. `ollama`, `openai`), `LLM_PROVIDER`, `RERANKER_PROVIDER`, así como las URIs y tokens de Milvus.
- **Factorías de Modelos**: Para que el endpoint no dependa fuertemente de una implementación (ej. local vs API), se utilizarán funciones factoría (`get_embeddings()`, `get_llm()`) que leerán la configuración e instanciarán la clase de Langchain correspondiente.

## Risks / Trade-offs

- **Risk: Endpoints más "pesados" (Fat Endpoints)** → *Mitigación*: Se extraerán las lógicas atómicas a funciones auxiliares o clases especializadas (ej. `document_processor.py`), pero el endpoint mantendrá la responsabilidad de llamar a cada función paso a paso.
- **Risk: Latencia por operaciones bloqueantes** → *Mitigación*: Asegurarse de que las llamadas a Milvus y a las APIs de embeddings se realicen de forma asíncrona (`async/await`) en el endpoint de FastAPI.
- **Risk: Configuración errónea al desplegar** → *Mitigación*: Definir valores por defecto seguros en el módulo de configuración y validar el `.env` al arranque de la aplicación usando Pydantic.
