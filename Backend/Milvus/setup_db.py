import sys
import os
import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pymilvus import MilvusClient, DataType

try:
    from config import conf
except ModuleNotFoundError:
    from Backend.config import conf

REGISTRY_COLLECTION = "_buckets_registry"
DEFAULT_VECTOR_DIM = 768

def create_bucket_collection(client: MilvusClient, bucket_name: str, dim: int = DEFAULT_VECTOR_DIM):
    """
    Crea una colección vectorial en Milvus con esquema estandarizado para documentos (Bucket).
    """
    collections = client.list_collections()
    if bucket_name not in collections:
        print(f"Creando colección/bucket '{bucket_name}' (dim={dim})...")
        schema = MilvusClient.create_schema(
            auto_id=True,
            enable_dynamic_field=True,
        )
        schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True)
        schema.add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=dim)
        schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=65535)
        schema.add_field(field_name="source_file", datatype=DataType.VARCHAR, max_length=255)
        schema.add_field(field_name="content_type", datatype=DataType.VARCHAR, max_length=100)
        schema.add_field(field_name="metadata", datatype=DataType.JSON)

        index_params = client.prepare_index_params()
        index_params.add_index(
            field_name="vector",
            index_type="AUTOINDEX",
            metric_type="COSINE"
        )
        index_params.add_index(
            field_name="content_type",
            index_type="INVERTED"
        )

        client.create_collection(
            collection_name=bucket_name,
            schema=schema,
            index_params=index_params
        )
        print(f"Colección '{bucket_name}' creada exitosamente.")
    else:
        print(f"La colección '{bucket_name}' ya existe.")

    # Cargar en memoria para búsquedas inmediatas
    try:
        client.load_collection(collection_name=bucket_name)
    except Exception as e:
        print(f"Nota: No se pudo cargar '{bucket_name}' en memoria aún: {e}")

def setup_registry(client: MilvusClient):
    """
    Crea la colección interna de registro de buckets en Milvus si no existe.
    """
    collections = client.list_collections()
    if REGISTRY_COLLECTION not in collections:
        print(f"Creando colección de metadatos de buckets '{REGISTRY_COLLECTION}'...")
        reg_schema = MilvusClient.create_schema(
            auto_id=False,
            enable_dynamic_field=True,
        )
        reg_schema.add_field(field_name="bucket_name", datatype=DataType.VARCHAR, max_length=128, is_primary=True)
        reg_schema.add_field(field_name="content_type", datatype=DataType.VARCHAR, max_length=100)
        reg_schema.add_field(field_name="description", datatype=DataType.VARCHAR, max_length=1000)
        reg_schema.add_field(field_name="created_at", datatype=DataType.VARCHAR, max_length=64)
        reg_schema.add_field(field_name="metadata", datatype=DataType.JSON)

        client.create_collection(
            collection_name=REGISTRY_COLLECTION,
            schema=reg_schema
        )
        print(f"Colección de registro '{REGISTRY_COLLECTION}' creada exitosamente.")
    
    try:
        client.load_collection(collection_name=REGISTRY_COLLECTION)
    except Exception as e:
        print(f"Nota: No se pudo cargar '{REGISTRY_COLLECTION}' en memoria: {e}")

def register_bucket_metadata(client: MilvusClient, bucket_name: str, content_type: str = "general", description: str = "", metadata: dict = None):
    """
    Registra o actualiza los metadatos de un bucket en la colección interna de registro.
    """
    data = [{
        "bucket_name": bucket_name,
        "content_type": content_type or "general",
        "description": description or "",
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "metadata": metadata or {}
    }]
    client.upsert(
        collection_name=REGISTRY_COLLECTION,
        data=data
    )

def setup_database():
    """
    Inicializa la base de datos 'MARIA', el registro de buckets y el bucket por defecto 'general'.
    """
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

    # 2. Asegurar colección de registro
    setup_registry(client)

    # 3. Asegurar bucket por defecto 'general'
    create_bucket_collection(client, "general", dim=DEFAULT_VECTOR_DIM)
    try:
        existing = client.get(
            collection_name=REGISTRY_COLLECTION,
            ids=["general"]
        )
        if not existing:
            register_bucket_metadata(
                client=client,
                bucket_name="general",
                content_type="general",
                description="Bucket general por defecto para almacenamiento de documentos",
                metadata={"default": True}
            )
    except Exception as e:
        print(f"Nota al registrar bucket 'general': {e}")

if __name__ == "__main__":
    setup_database()
