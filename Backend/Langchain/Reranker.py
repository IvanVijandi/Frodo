## Modulo para el reranker
import voyageai
import os

class Reranker:
    def __init__(self):
        self.client = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))
    
    def  rerank(self,query: str, document: list[dict]):
        
        lista_chunks = []
        
        for hit in document:
            # hit es un objeto Hit de PyMilvus que se comporta como diccionario
            chunk = hit['entity']['text_chunk']
            lista_chunks.append(chunk)
        
        response = self.client.rerank(
            model="rerank-2",
            query=query,
            documents=lista_chunks,
            top_k=3
        )
        
        lista_response = []
        
        for r in response.results:
            # r.index nos dice en qué posición estaba este resultado en la lista original
            original_hit = document[r.index]
            lista_response.append(original_hit)
            
        return lista_response