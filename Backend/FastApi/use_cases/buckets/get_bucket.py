from typing import Dict, Any, Optional

class GetBucketUseCase:
    """Caso de uso para consultar información detallada de un bucket."""

    def __init__(self, milvus_client):
        self.milvus_client = milvus_client

    async def execute(self, bucket_name: str) -> Optional[Dict[str, Any]]:
        bucket_info = await self.milvus_client.get_bucket(bucket_name)
        return bucket_info

