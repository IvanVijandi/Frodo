from typing import Optional, Dict, Any

class CreateBucketUseCase:
    """Caso de uso para crear un nuevo bucket temático en Milvus y sincronizarlo en PostgreSQL."""
    
    def __init__(self, milvus_client, db=None):
        self.milvus_client = milvus_client
        self.db = db

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

        # Sincronizar en PostgreSQL si la sesión está disponible
        if self.db:
            try:
                from Postgres import repository
                existing = await repository.get_bucket_by_name(self.db, bucket_info["name"])
                if not existing:
                    pg_b = await repository.create_bucket(
                        db=self.db,
                        name=bucket_info["name"],
                        content_type=bucket_info["content_type"],
                        description=bucket_info.get("description", ""),
                        extra_metadata=bucket_info.get("metadata", {})
                    )
                    bucket_info["id"] = str(pg_b.id)
                else:
                    bucket_info["id"] = str(existing.id)
            except Exception as e:
                print(f"Nota: No se pudo sincronizar bucket en Postgres: {e}")

        return {
            "message": f"Bucket '{bucket_info['name']}' creado exitosamente.",
            "bucket": bucket_info
        }

