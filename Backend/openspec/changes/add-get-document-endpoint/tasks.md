# Tasks: Add /get-document Endpoint

- [x] 1. En `FastApi/main.py`, importar `BaseModel` de Pydantic y crear una clase `QueryRequest` con un campo `query: str` y `pdf_ids: Optional[list[int]]`.
- [x] 2. Crear el endpoint `@app.post("/get-document")` que reciba `request: QueryRequest` y las dependencias `milvus_client` y `embedding_generator`.
- [x] 3. Dentro del endpoint, generar el embedding de la query usando `await embedding_generator.get_query_embedding(request.query)`.
- [x] 4. Realizar la búsqueda vectorial llamando a `await milvus_client.get_document(query_vector=query_vector, collection_name="documentos", ids=request.pdf_ids)`.
- [x] 5. Retornar la lista de resultados encontrados al usuario.
