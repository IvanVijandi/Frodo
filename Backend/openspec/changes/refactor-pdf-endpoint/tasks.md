## 1. Configuración Dinámica (Dynamic Model Config)

- [x] 1.1 Crear el archivo `.env` base (o `.env.example`) con las variables: `EMBEDDING_PROVIDER`, `LLM_PROVIDER`, `MILVUS_URI`, `MILVUS_TOKEN` y configuraciones específicas de Ollama/OpenAI.
- [x] 1.2 Implementar o actualizar el módulo de configuración (`config.py` o similar) para cargar y validar estas variables (usando `pydantic-settings` si aplica).
- [x] 1.3 Crear factorías (`factories.py` o dentro de `config.py`) para devolver la instancia adecuada de LLM (`get_llm()`) y Embeddings (`get_embeddings()`) según el provider configurado.

## 2. Refactorización del Procesamiento (PDF Upload Processing)

- [x] 2.1 Refactorizar la lógica de lectura y partición (splitting) de texto para que sea invocable independientemente (ej. `extract_text_and_split(file_path)`).
- [x] 2.2 Preparar la función para inyectar y almacenar los vectores generados en Milvus utilizando el cliente expuesto.

## 3. Integración en FastAPI (PDF Sequential Endpoint)

- [x] 3.1 Actualizar el router de carga de PDFs (`routers/` o equivalente) para manejar la subida del archivo.
- [x] 3.2 Inyectar en el endpoint las dependencias necesarias: configuración, factoría de embeddings, cliente de Milvus.
- [x] 3.3 Implementar la secuencia en el endpoint: guardar el archivo temporalmente, llamar a la extracción/splitting, generar embeddings con la factoría y guardar en Milvus de manera asíncrona.
- [x] 3.4 Capturar errores en cada paso del proceso secuencial y devolver códigos HTTP adecuados (400, 500).

## 4. Limpieza (Cleanup)

- [x] 4.1 Eliminar o simplificar `pdf_service.py` removiendo la lógica duplicada.
- [x] 4.2 Asegurar que la aplicación principal inicie correctamente con las nuevas configuraciones y dependencias (ej. testing manual del endpoint usando Swagger UI).
