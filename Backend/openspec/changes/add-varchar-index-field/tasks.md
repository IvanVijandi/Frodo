# Implementation Tasks

- `[x]` 1. Modificar el archivo `Milvus/setup_db.py`.
    - Agregar el campo `entity_group` de tipo VARCHAR al esquema con `max_length` (por ejemplo, 255).
- `[x]` 2. Agregar la definición del índice escalar para el campo `entity_group` usando `index_type="Trie"` dentro de la función `setup_database()`.
- `[x]` 3. Opcionalmente (según se necesite en las queries), revisar los archivos de Ingesta (e.g., `Langchain/Splitter.py` o scripts similares) para asegurarse de que el campo sea populado correctamente al añadir documentos.
