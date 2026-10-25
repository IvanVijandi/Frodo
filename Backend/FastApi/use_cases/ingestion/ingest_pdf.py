import os
import tempfile
from typing import Optional, Dict, Any

try:
    from Langchain.Splitter import Splitter
except ModuleNotFoundError:
    from Backend.Langchain.Splitter import Splitter

class IngestPdfUseCase:
    """Caso de uso para procesar, fragmentar, vectorizar e indexar un PDF en Milvus."""

    def __init__(self, milvus_client, embedding_generator):
        self.milvus_client = milvus_client
        self.embedding_generator = embedding_generator
        self.splitter = Splitter()

    async def execute(
        self,
        file_bytes: bytes,
        filename: str,
        bucket_name: str = "general",
        content_type: Optional[str] = None
    ) -> Dict[str, Any]:
        if not filename.lower().endswith(".pdf"):
            raise ValueError("Solo se admiten archivos con extensión PDF (.pdf).")

        target_bucket = bucket_name.strip() if bucket_name else "general"

        # 1. Asegurar existencia del bucket en Milvus
        if not await self.milvus_client.bucket_exists(target_bucket):
            await self.milvus_client.create_bucket(
                name=target_bucket,
                content_type=content_type or "general",
                description=f"Bucket autogenerado para {target_bucket}"
            )

        # 2. Resolver content_type efectivo
        resolved_content_type = content_type
        if not resolved_content_type:
            bucket_info = await self.milvus_client.get_bucket(target_bucket)
            resolved_content_type = bucket_info.get("content_type", "general") if bucket_info else "general"

        tmp_path = None
        try:
            # 3. Guardar archivo temporal
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(file_bytes)
                tmp_path = tmp.name

            # 4. Extraer y dividir texto
            docs = self.splitter.split_document(tmp_path)
            if not docs:
                raise ValueError("El documento PDF está vacío o no se pudo extraer texto.")

            for doc in docs:
                if 'metadata' not in doc:
                    doc['metadata'] = {}
                doc['metadata']["source_file"] = filename
                doc['metadata']["bucket"] = target_bucket
                doc['metadata']["content_type"] = resolved_content_type

            # 5. Generar embeddings
            text_chunks = [doc['text'] for doc in docs]
            vector_chunks = await self.embedding_generator.get_document_embedding(text_chunks)

            # 6. Formatear e insertar en Milvus
            data_to_insert = self.embedding_generator.format_database(
                text_chunks=docs,
                vector_chunks=vector_chunks,
                content_type=resolved_content_type
            )
            await self.milvus_client.upload_document(data=data_to_insert, collection_name=target_bucket)

            return {
                "message": "Archivo cargado y procesado con éxito.",
                "bucket": target_bucket,
                "content_type": resolved_content_type,
                "chunks_procesados": len(docs)
            }

        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)

