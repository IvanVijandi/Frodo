from typing import Dict, Any, Optional

class SearchDocumentsUseCase:
    """Caso de uso para búsqueda semántica vectorial y reranking en un bucket de Milvus."""

    def __init__(self, milvus_client, embedding_generator, reranker: Optional[Any] = None):
        self.milvus_client = milvus_client
        self.embedding_generator = embedding_generator
        self.reranker = reranker

    async def execute(self, query: str, bucket_name: str = "general") -> Dict[str, Any]:
        target_bucket = bucket_name.strip() if bucket_name else "general"

        if not await self.milvus_client.bucket_exists(target_bucket):
            raise KeyError(f"El bucket '{target_bucket}' no existe.")

        query_vector = await self.embedding_generator.get_query_embedding(query)
        results = await self.milvus_client.get_document(
            query_vector=query_vector,
            collection_name=target_bucket
        )

        if self.reranker is not None and len(results) > 0 and results[0]:
            final_results = self.reranker.rerank(query, results)
            msg = f"Búsqueda y reranking realizados en bucket '{target_bucket}'."
        else:
            final_results = results
            msg = f"Búsqueda realizada en bucket '{target_bucket}'."

        return {
            "message": msg,
            "bucket": target_bucket,
            "results": final_results
        }

