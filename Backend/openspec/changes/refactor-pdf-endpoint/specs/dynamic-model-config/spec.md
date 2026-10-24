## ADDED Requirements

### Requirement: Carga de configuración dinámica
El sistema SHALL cargar las variables de configuración referentes a modelos, APIs y bases de datos a partir de un archivo `.env` o el entorno del sistema, proveyendo valores por defecto seguros.

#### Scenario: Entorno de ejecución local
- **WHEN** el sistema arranca.
- **THEN** lee las variables (ej. `EMBEDDING_PROVIDER`, `LLM_PROVIDER`) del archivo `.env` o entorno y las utiliza para instanciar los respectivos clientes de modelos (ej. locales a través de Ollama, o externos mediante API key).

### Requirement: Factoría de proveedores
El sistema SHALL instanciar el proveedor de embeddings, reranker o LLM basándose en la configuración.

#### Scenario: Cambio de modelo sin alterar código
- **WHEN** un administrador cambia `EMBEDDING_PROVIDER=openai` en el archivo `.env`.
- **THEN** el sistema automáticamente instancia `OpenAIEmbeddings` en lugar de `OllamaEmbeddings` para las subsecuentes operaciones de PDF sin requerir cambios de código.
