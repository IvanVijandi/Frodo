from pymilvus import MilvusClient, DataType, AsyncMilvusClient

from ..config import conf 
  
class Async_Milvus_Client:
    
    "Clase para el cliente asíncrono de la bsdd estudia_db en Milvus."
    
    def __init__(self):
        self.client = AsyncMilvusClient(uri=conf.MILVUS_URI, db_name="estudia_db")
    
    async def delete_documents(self, collection_name: str, ids: list[int]):
        return await self.client.delete(
            collection_name=collection_name,
            ids=ids
        )

    async def upload_document(self,data: list[dict], collection_name : str,  ):
        
        res = await self.client.insert(
            collection_name = collection_name,
            data = data
        )
    
        print(f"resultado de la insercion: {res}, en la coleccion: {collection_name}")


    async def get_document(self, query_vector: list[float], collection_name: str, filter: str = "", ids: list[int] = None):
        
        # Construir filtro por IDs si se proporcionan
        if ids and len(ids) > 0:
            ids_filter = f"pdf_id in {ids}"
            # Combinar con filtro existente si lo hay
            final_filter = f"({filter}) and ({ids_filter})" if filter else ids_filter
        else:
            final_filter = filter
        
        res = await self.client.search(
            collection_name=collection_name,
            anns_field = "vector_chunk",
            data = [query_vector],
            limit = 5,
            search_params={"metric_type":"COSINE"},
            filter = final_filter,
            output_fields = ["text_chunk", "pdf_id"]
        )
        
        lista = []
        
        for hits in res:
            for hit in hits:
                lista.append(hit)
        
        print(f"Documentos encontrados con filtro '{final_filter}': {len(lista)}")     
        return lista

                      
class Milvus_Sync_Client:   
    
    def __init__(self):
        self.client = MilvusClient(uri=conf.MILVUS_URI, db_name="estudia_db") 
              
    def create_milvus_collection(self,name: str):
        
        """"Crea una coleccion en Milvus con el esquema e indices definidos."""
        
        if name in self.client.list_collections():
            
            print(f"La coleccion {name} ya existe")
            return None
        
        # <-- Esquema -->
        schema = MilvusClient.create_schema(
            auto_id=True,
            enable_dynamic_field=True,
        )

        schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True, auto_id=True)
        schema.add_field(field_name="vector_chunk", datatype=DataType.FLOAT_VECTOR, dim=3072) ##dim 1536 | recomendada para Gemini
        schema.add_field(field_name="text_chunk", datatype=DataType.VARCHAR, max_length=2000)
        schema.add_field(field_name="pdf_id", datatype=DataType.INT64)  # Campo para filtrar por PDF
        schema.add_field(field_name="metadata", datatype=DataType.JSON, nullable=True) ##Datos adicionales que sirven para filtrar la busqueda

        ## <-- Indices -->
        index_params = self.client.prepare_index_params()


        index_params.add_index(
            field_name="vector_chunk", 
            index_type="HNSW",  ##Prepara un grafo con los vecinos mas cercanos | Pesadito (hay que evaluarlo)
            index_name="vector_index", 
            metric_type="COSINE",
            params={
                "M": 16, 
                "efConstruction": 256
            } 
        )
        
        index_params.add_index(
            field_name="text_chunk",
            index_type="INVERTED"  # Recomendado para VARCHAR
            
        )
        

        collection = self.client.create_collection(
            collection_name=name,
            schema=schema,
            index_params=index_params
        )

        ##Cargamos la coleccion en memoria
        res = self.client.get_load_state(
            collection_name=name
        )

        print(res)
        
    def remove_collection(self, name_collection: str):
         self.client.drop_collection(
            collection_name=name_collection
        )
    
    def close(self):
        self.client.close()

def check_database_exist():
    
    """Verifica si la base de datos 'estudia_db' existe en Milvus, si no, la crea."""
    
    client = MilvusClient(uri=conf.MILVUS_URI)

    if "estudia_db" not in client.list_databases():
            
        client.create_database("estudia_db")
        
    else:
        print(f"La base de datos {"estudia_db"} ya existe")
    
    client.close() 
    

##Instancias de clientes y verificacion de base de datos
check_database_exist()

syncClient = Milvus_Sync_Client()
syncClient.create_milvus_collection("documents_collection")
syncClient.close()

