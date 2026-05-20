## Context

Actualmente, el sistema MARIA-1 (un sistema basado en arquitectura RAG) no cuenta con un mecanismo para ingerir directamente documentos de conocimiento proporcionados por el usuario. El objetivo es crear una vía para recibir archivos PDF, que suelen ser el formato más común de intercambio de documentos de texto, procesarlos (text splitting), generar sus representaciones vectoriales (embeddings) a través de modelos locales con Ollama, y almacenarlos en la base de datos vectorial Milvus para su posterior recuperación.

## Goals / Non-Goals

**Goals:**
- Proveer un endpoint `/upload-file` en FastAPI que reciba un archivo PDF.
- Extraer correctamente el texto del documento PDF.
- Dividir el texto en fragmentos (chunks) usando una estrategia que preserve el contexto semántico (ej. `RecursiveCharacterTextSplitter` de Langchain).
- Generar embeddings de cada fragmento utilizando un modelo de Ollama.
- Insertar los vectores resultantes, junto con la información de origen (metadatos como nombre de archivo, página), en una colección de Milvus.

**Non-Goals:**
- Soporte para la extracción de texto a partir de imágenes escaneadas dentro de los PDFs (OCR) en esta primera versión.
- Soporte para otros formatos de archivo (como Word, Excel, TXT), lo cual quedará para iteraciones futuras.
- Procesamiento asíncrono avanzado con colas (ej. Celery/RabbitMQ) para la carga masiva de archivos muy grandes; por ahora el procesamiento será síncrono en el mismo endpoint.

## Decisions

1. **Librería de procesamiento de PDF:** Se utilizará `PyPDFLoader` de Langchain (que internamente usa `pypdf`).
   - *Rationale:* Está nativamente integrada en Langchain, lo cual facilita el flujo de trabajo (Document Loading -> Splitting).
2. **Estrategia de Text Splitting:** `RecursiveCharacterTextSplitter` de Langchain.
   - *Rationale:* Es la recomendación estándar para documentos de texto general, ya que intenta mantener juntos los párrafos y oraciones antes de dividir por caracteres duros.
3. **Generación de Embeddings:** `OllamaEmbeddings` de Langchain.
   - *Rationale:* Permite generar embeddings localmente utilizando el stack tecnológico ya definido, asegurando consistencia con el resto del pipeline.
4. **Almacenamiento en Milvus:** Se utilizará el conector de `Milvus` proveído por Langchain.
   - *Rationale:* Simplifica la creación de la colección y la inserción de documentos y sus embeddings.

## Risks / Trade-offs

- **[Riesgo] Tiempos de respuesta lentos por procesamiento síncrono:** Si el archivo PDF es muy grande, extraer el texto y generar los embeddings puede causar un timeout en el endpoint.
  - *Mitigación:* Para esta versión inicial, se asume que los PDFs tendrán un tamaño manejable. A futuro, se puede migrar a un procesamiento asíncrono en background donde el endpoint devuelva un `job_id`.
- **[Riesgo] Calidad de los chunks:** La división automática puede cortar frases a la mitad, afectando la calidad del embedding.
  - *Mitigación:* Se configurará un `chunk_overlap` adecuado en el text splitter para retener algo de contexto entre fragmentos adyacentes.
