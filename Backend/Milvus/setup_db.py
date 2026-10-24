import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pymilvus import MilvusClient, DataType

try:
    from config import conf
except ModuleNotFoundError:
    from Backend.config import conf

def setup_database():
    print(f"Conectando a Milvus en {conf.MILVUS_URI}...")
    client = MilvusClient(uri=conf.MILVUS_URI)
    
    # 1. Asegurar base de datos
    databases = client.list_databases()
    if "MARIA" not in databases:
        print("Creando base de datos 'MARIA'...")
        client.create_database("MARIA")
        print("Base de datos 'MARIA' creada exitosamente.")
    else:
        print("La base de datos 'MARIA' ya existe.")
        
    client.using_database("MARIA")
    
    # 2. Asegurar colección
    collections = client.list_collections()
    if "documentos" not in collections:
        print("Creando colección 'documentos' con schema...")
        schema = MilvusClient.create_schema(
            auto_id=True,
            enable_dynamic_field=True,
        )
        schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True)
        schema.add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=1024)
        schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=65535)
        schema.add_field(field_name="source_file", datatype=DataType.VARCHAR, max_length=255)
        schema.add_field(field_name="prestacion", datatype=DataType.VARCHAR, max_length=255)
        
        index_params = client.prepare_index_params()
        index_params.add_index(
            field_name="vector",
            index_type="AUTOINDEX",
            metric_type="COSINE"
        )
        index_params.add_index(
            field_name="prestacion",
            index_type="INVERTED"
        )
        
        client.create_collection(
            collection_name="documentos",
            schema=schema,
            index_params=index_params
        )
        print("Colección 'documentos' creada exitosamente.")
    else:
        print("La colección 'documentos' ya existe.")
        
    # 3. Cargar la colección en memoria para que esté disponible para búsquedas
    try:
        client.load_collection(collection_name="documentos")
        print("Colección 'documentos' cargada exitosamente en memoria.")
    except Exception as e:
        print(f"Nota: No se pudo cargar la colección en memoria (podría estar vacía aún): {e}")

if __name__ == "__main__":
    setup_database()
