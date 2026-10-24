from pymilvus import MilvusClient, DataType, AsyncMilvusClient

try:
    from config import conf 
except ModuleNotFoundError:
    from Backend.config import conf
  
class Async_Milvus_Client:
    
    "Clase para el cliente asíncrono de la bsdd estudia_db en Milvus."
    
    def __init__(self):
        self.client = AsyncMilvusClient(uri=conf.MILVUS_URI, db_name="MARIA")
        
    async def get_document(self, query_vector: list[float], collection_name: str, limit: int = 10, filter: str = None) -> list[dict]:
        "Devuelve una lista de los documentos mas similares a la query dada"
        
        results = await self.client.search(
            collection_name=collection_name,
            data=[query_vector],
            anns_field="vector",
            search_params={"metric_type": "COSINE"},
            limit=limit,
            filter=filter,
            output_fields=["text", "source_file", "id", "prestacion"]
        )
        return results
    
    async def upload_document(self, data: list[dict], collection_name: str):
        "Sube un documento a la bsdd"
        
        insert_results = await self.client.insert(
            collection_name=collection_name,
            data=data
        )
        return insert_results
