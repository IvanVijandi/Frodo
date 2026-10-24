# Design: Add /get-document Endpoint

## Architecture
1. **Endpoint FastAPI**: Se agregará una ruta `POST /get-document` en `FastApi/main.py`.
2. **Modelo de Datos Pydantic**: Se definirá un modelo para parsear el body del request. Se llamará `QueryRequest` e incluirá:
   - `query`: string (requerido). El texto a buscar.
   - `pdf_ids`: lista de enteros (opcional). Permite filtrar la búsqueda a ciertos documentos específicos.
3. **Flujo de Ejecución**:
   - El endpoint recibe la `QueryRequest`.
   - Llama a `await embedding_generator.get_query_embedding(request.query)` para transformar el string de texto a su representación vectorial.
   - Llama a `await milvus_client.get_document(query_vector=vector, collection_name="documentos", ids=request.pdf_ids)`.
   - Retorna los resultados formateados al cliente (cada resultado de Milvus incluye el `text_chunk` y el `pdf_id`).

## Alternatives Considered
- **Usar el método GET**: Se podría haber usado `GET /get-document?query=...`. Sin embargo, las consultas a un motor RAG pueden ser textos largos (párrafos enteros) o incluir parámetros de filtrado complejos (ej. múltiples IDs). El método `POST` con body JSON permite enviar datos largos y estructurados de forma mucho más limpia.
