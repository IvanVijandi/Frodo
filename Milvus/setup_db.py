import sys
import os

# Añadir el directorio raíz al path para poder importar config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymilvus import MilvusClient, DataType
from config import conf

def setup_database():
    print(f"Conectando a Milvus en {conf.MILVUS_URI}...")
    client = MilvusClient(uri=conf.MILVUS_URI)
    
    # Asegurar que existe la base de datos MARIA
    databases = client.list_databases()
    if "MARIA" not in databases:
        print("Creando base de datos 'MARIA'...")
        client.create_database("MARIA")
    
    # Reconectar apuntando a la base de datos MARIA
    client = MilvusClient(uri=conf.MILVUS_URI, db_name="MARIA")
    
    collection_name = "documentos"
    
    if client.has_collection(collection_name):
        print(f"La colección '{collection_name}' ya existe. Borrándola para aplicar el nuevo esquema...")
        client.drop_collection(collection_name)
    
    print("Definiendo esquema de la colección...")
    schema = client.create_schema(auto_id=True, enable_dynamic_field=False)
    
    # 1. Campo ID auto-generado como clave primaria
    schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True, description="Clave primaria auto-generada para cada chunk")
    
    # 2. ID del PDF (se ingresa manualmente para agrupar los chunks por archivo)
    schema.add_field(field_name="pdf_id", datatype=DataType.INT64, description="ID del documento PDF al que pertenece el chunk")
    
    # 3. Vector chunk
    schema.add_field(field_name="vector_chunk", datatype=DataType.FLOAT_VECTOR, dim=768, description="Vector de embedding")
    
    # 4. Text chunk
    schema.add_field(field_name="text_chunk", datatype=DataType.VARCHAR, max_length=2000, description="Contenido de texto del chunk")
    
    # 5. Metadata como tipo JSON dinámico
    schema.add_field(field_name="metadata", datatype=DataType.JSON, description="Metadatos en formato JSON")
    
    print("Creando parámetros de índice para 'vector_chunk'...")
    index_params = client.prepare_index_params()
    index_params.add_index(
        field_name="vector_chunk",
        metric_type="COSINE",
        index_type="IVF_FLAT",
        params={"nlist": 128}
    )
    
    print(f"Creando la colección '{collection_name}'...")
    client.create_collection(
        collection_name=collection_name,
        schema=schema,
        index_params=index_params
    )
    
    print(f"¡Colección '{collection_name}' creada exitosamente con el nuevo esquema!")
    
    # Mostrar la descripción de la nueva colección
    desc = client.describe_collection(collection_name)
    print("\nEsquema de la colección:")
    print(desc)

if __name__ == "__main__":
    setup_database()
