from pymilvus import MilvusClient, DataType, AsyncMilvusClient

from config import conf 
  
class Async_Milvus_Client:
    
    "Clase para el cliente asíncrono de la bsdd estudia_db en Milvus."
    
    def __init__(self):
        self.client = AsyncMilvusClient(uri=conf.MILVUS_URI, db_name="MARIA")
    
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


    async def get_document(self, query_vector: list[float], collection_name: str, filter: str = ""):
        
        final_filter = filter
        
        res = await self.client.search(
            collection_name=collection_name,
            anns_field = "vector_chunk",
            data = [query_vector],
            limit = 5,
            search_params={"metric_type":"COSINE"},
            filter = final_filter,
            output_fields = ["text_chunk"]
        )
        
        lista = []
        
        for hits in res:
            for hit in hits:
                lista.append(hit)
        
        print(f"Documentos encontrados con filtro '{final_filter}': {len(lista)}")     
        return lista

                      


