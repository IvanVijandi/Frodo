## Modulo para el reranker
import voyageai
import os

class Reranker:
    def __init__(self):
        self.client = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))
    
    def  rerank(self,query: str, document: list[dict]):
        
        lista_chunks = []
        
        for i in document:
            for j in i:
                chunk = j['entity']['text_chunk']
                lista_chunks.append(chunk)
        
        response = self.client.rerank(
            model="rerank-2.5-lite",
            query=query,
            documents=lista_chunks,
            top_k=3
        )
        
        lista_response = []
        
        for r in response.results:
            lista_response.append(r.document)
            
        return lista_response
            