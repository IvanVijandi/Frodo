# Design

## Schema Changes
En el archivo `Milvus/setup_db.py`, se modificará el esquema de la colección de Milvus.
- Agregar un campo VARCHAR: `schema.add_field(field_name="entity_group", datatype=DataType.VARCHAR, max_length=255, description="Campo escalar para filtrado optimizado")`.
- El nombre `entity_group` es propuesto pero puede ser modificado por el usuario si lo desea.

## Indexing
Para optimizar las búsquedas basadas en este campo, definiremos un índice escalar.
- En versiones recientes de PyMilvus, los índices sobre campos escalares se agregan directamente al objeto `index_params`.
- Agregaremos:
```python
index_params.add_index(
    field_name="entity_group",
    index_type="Trie"
)
```
- Esto permitirá realizar búsquedas con prefijos o filtrado exacto usando `expr` en las operaciones de búsqueda de forma altamente eficiente.
