from typing import Dict, Any, List

class ListBucketsUseCase:
    """Caso de uso para listar todos los buckets registrados en Milvus."""

    def __init__(self, milvus_client):
        self.milvus_client = milvus_client

    async def execute(self) -> Dict[str, List[Dict[str, Any]]]:
        buckets = await self.milvus_client.list_buckets()
        return {"buckets": buckets}

