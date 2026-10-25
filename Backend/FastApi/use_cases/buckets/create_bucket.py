from typing import Optional, Dict, Any

class CreateBucketUseCase:
    """Caso de uso para crear un nuevo bucket temático en Milvus."""
    
    def __init__(self, milvus_client):
        self.milvus_client = milvus_client

    async def execute(
        self,
        name: str,
        content_type: str = "general",
        description: Optional[str] = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        if not name or not name.strip():
            raise ValueError("El nombre del bucket no puede estar vacío.")

        bucket_info = await self.milvus_client.create_bucket(
            name=name.strip(),
            content_type=content_type or "general",
            description=description or "",
            metadata=metadata or {}
        )
        return {
            "message": f"Bucket '{bucket_info['name']}' creado exitosamente.",
            "bucket": bucket_info
        }

