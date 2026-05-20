# Proposal: Add /get-document Endpoint

## What
Crear un nuevo endpoint `/get-document` en la API de FastAPI que reciba una consulta (query) de texto, genere su embedding vectorial y busque en la base de datos de Milvus los chunks de texto más relevantes utilizando búsqueda vectorial.

## Why
Actualmente el sistema permite cargar documentos (`/upload-file`) y procesarlos en la base de datos vectorial (Milvus). Sin embargo, aún no hay un punto de acceso en la API para consultar esta información y recuperar conocimiento. Este endpoint completará el flujo básico de Recuperación de Información (Retrieval) para el motor RAG, usando la función `get_document` ya definida en el cliente de Milvus.
