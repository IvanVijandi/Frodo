## ADDED Requirements

### Requirement: Flujo secuencial de procesamiento en Endpoint
El sistema SHALL ejecutar el procesamiento de carga de PDFs de manera secuencial dentro del mismo endpoint de FastAPI, sin delegar el flujo de control completo a un servicio de caja negra. El endpoint debe inyectar/instanciar las dependencias y coordinar los pasos (extracción de texto, fragmentación, generación de embeddings, almacenamiento).

#### Scenario: Procesamiento paso a paso
- **WHEN** un archivo PDF es recibido en el endpoint.
- **THEN** el endpoint llama a las funciones de extracción de texto, fragmentación (splitting) y generación de embeddings (una tras otra), y finalmente guarda los resultados en Milvus, permitiendo capturar errores y retornar un estado preciso en cada paso.
