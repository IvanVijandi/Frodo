from typing import Dict, Any

class DeleteBucketUseCase:
    """Caso de uso para eliminar un bucket y su colección vectorial física."""

    def __init__(self, milvus_client):
        self.milvus_client = milvus_client

    async def execute(self, bucket_name: str) -> Dict[str, Any]:
        if bucket_name == "general":
            raise ValueError("El bucket 'general' está protegido y no puede ser eliminado.")

        await self.milvus_client.delete_bucket(bucket_name)
        return {"message": f"Bucket '{bucket_name}' eliminado exitosamente."}

