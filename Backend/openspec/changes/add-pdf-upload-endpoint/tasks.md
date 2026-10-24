## 1. Setup y Dependencias

- [x] 1.1 Verificar e instalar las dependencias requeridas para el procesamiento de PDFs y vectores (ej. `pypdf`, `pymupdf`, integración de Milvus para Langchain) en el entorno.
- [x] 1.2 Configurar la inicialización de la conexión con Milvus dentro del sistema.
- [x] 1.3 Configurar `OllamaEmbeddings` para que apunte al servicio local de Ollama.

## 2. Lógica de Procesamiento de PDF

- [x] 2.1 Implementar un mecanismo (función o servicio) para guardar temporalmente el archivo subido, ya que `PyPDFLoader` requiere un path de archivo físico.
- [x] 2.2 Implementar la lógica para extraer el texto utilizando `PyPDFLoader`.
- [x] 2.3 Aplicar `RecursiveCharacterTextSplitter` sobre los documentos extraídos para dividirlos en chunks manejables (ej. 1000 caracteres, con 200 de solapamiento).

## 3. Integración Vectorial

- [x] 3.1 Implementar la lógica que toma los chunks, usa `OllamaEmbeddings` para generar los vectores y guarda los documentos en Milvus usando `Milvus` de Langchain.
- [x] 3.2 Asegurar que el archivo PDF temporal se elimine del sistema de archivos una vez completada la inserción para no consumir espacio innecesario.

## 4. Endpoint FastAPI

- [x] 4.1 Crear el endpoint `POST /upload-file` en FastAPI que acepte `UploadFile`.
- [x] 4.2 Añadir validación para asegurar que el archivo cargado sea estrictamente un PDF. Retornar error HTTP 400/415 si no lo es.
- [x] 4.3 Integrar el flujo completo: validación -> guardado temporal -> extracción y split -> embeddings y subida a Milvus -> limpieza -> respuesta al cliente.

## 5. Pruebas y Verificación

- [x] 5.1 Realizar prueba enviando un documento PDF de prueba vía Swagger UI o cURL.
- [x] 5.2 Verificar a través de Attu (o consultando directamente a Milvus) que los vectores se han guardado junto a sus metadatos (ej. source).
