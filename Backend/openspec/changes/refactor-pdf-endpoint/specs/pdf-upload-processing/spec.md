## MODIFIED Requirements

### Requirement: Extracción de texto y almacenamiento vectorial
El sistema SHALL extraer todo el texto disponible en el archivo PDF, dividirlo en fragmentos (chunks) de texto de tamaño configurado, generar un embedding vectorial para cada fragmento usando el modelo de lenguaje configurado dinámicamente en el sistema (ej. Ollama, OpenAI, etc.), y almacenar dichos vectores junto con metadatos relevantes en una colección de Milvus. Toda esta lógica será coordinada desde el router/endpoint y no oculta en un servicio monolítico.

#### Scenario: Procesamiento completo del documento
- **WHEN** el PDF es aceptado por el endpoint.
- **THEN** el sistema usa un cargador para obtener el texto, lo divide utilizando una estrategia que preserve el contexto semántico, obtiene los vectores a través de la factoría de embeddings (según configuración) y los inserta exitosamente en Milvus gestionando de forma secuencial cada operación.
