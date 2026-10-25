from typing import Dict, Any

class DeleteBucketUseCase:
    """Caso de uso para eliminar un bucket y su colección vectorial física y relacional."""

    def __init__(self, milvus_client, db=None):
        self.milvus_client = milvus_client
        self.db = db

    async def execute(self, bucket_name: str) -> Dict[str, Any]:
        if bucket_name == "general":
            raise ValueError("El bucket 'general' está protegido y no puede ser eliminado.")

        await self.milvus_client.delete_bucket(bucket_name)

        if self.db:
            try:
                from Postgres import repository
                await repository.delete_bucket_by_name(self.db, bucket_name)
            except Exception as e:
                print(f"Nota: No se pudo eliminar bucket de Postgres: {e}")

        return {"message": f"Bucket '{bucket_name}' eliminado exitosamente."}

