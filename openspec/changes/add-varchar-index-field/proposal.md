# Proposal: Agregar campo VARCHAR indexado

## What
Se propone agregar un nuevo campo escalar de tipo VARCHAR al esquema de la colección "documentos" en la base de datos Milvus. El nombre propuesto por defecto es `entity_group` (o el que el usuario prefiera).

## Why
El objetivo es permitir que múltiples chunks compartan el mismo valor (por ejemplo, agrupar por categoría, identificador de cliente o tipo de entidad). Crear un índice escalar sobre este campo permitirá realizar un filtrado previo (pre-filtering) durante las búsquedas vectoriales, optimizando significativamente la velocidad de búsqueda.
