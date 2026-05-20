## ADDED Requirements

### Requirement: Carga de archivo PDF
El sistema SHALL proveer un endpoint HTTP POST en la ruta `/upload-file` que acepte un archivo en formato PDF (multipart/form-data).

#### Scenario: Carga exitosa de un PDF válido
- **WHEN** un cliente hace una petición POST a `/upload-file` incluyendo un archivo PDF válido.
- **THEN** el sistema acepta el archivo, inicia su procesamiento y retorna un código HTTP 200 con un mensaje de éxito indicando que el archivo fue cargado y procesado.

#### Scenario: Carga de archivo con formato no soportado
- **WHEN** un cliente hace una petición POST a `/upload-file` con un archivo que no tenga extensión o tipo de contenido PDF (por ejemplo, un .txt o .docx).
- **THEN** el sistema rechaza la petición y retorna un código de error HTTP 400 (Bad Request) o 415 (Unsupported Media Type), indicando que solo se admiten archivos PDF.

### Requirement: Extracción de texto y almacenamiento vectorial
El sistema SHALL extraer todo el texto disponible en el archivo PDF, dividirlo en fragmentos (chunks) de texto de tamaño configurado, generar un embedding vectorial para cada fragmento usando un modelo de lenguaje local (Ollama), y almacenar dichos vectores junto con metadatos relevantes en una colección de Milvus.

#### Scenario: Procesamiento completo del documento
- **WHEN** el PDF es aceptado por el endpoint.
- **THEN** el sistema usa un cargador (ej. PyPDFLoader) para obtener el texto, lo divide utilizando una estrategia que preserve el contexto semántico (ej. RecursiveCharacterTextSplitter), obtiene los vectores a través de OllamaEmbeddings y los inserta exitosamente en Milvus.
