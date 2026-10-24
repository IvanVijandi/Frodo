import os
import sys

try:
    from config import conf
except ModuleNotFoundError:
    from Backend.config import conf

from langchain_ollama import OllamaEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings

class EmbeddingGenerator:
    def __init__(self):
        provider = conf.EMBEDDING_PROVIDER.lower()
        if provider == "ollama":
            self.model = OllamaEmbeddings(
                base_url=conf.OLLAMA_URI,
                model=conf.EMBEDDING_MODEL
            )
        elif provider == "google":
            self.model = GoogleGenerativeAIEmbeddings(
                api_key=conf.GEMINI_API_KEY,
                model=conf.EMBEDDING_MODEL or "gemini-embedding-001",
                output_dimensionality=conf.VECTOR_DIM,
                task_type="RETRIEVAL_DOCUMENT"
            )
        else:
            raise ValueError(f"Proveedor de embeddings '{provider}' no soportado.")

    async def get_document_embedding(self, text: list[str]) -> list[list[float]]:
        """Genera embeddings para una lista de textos (documentos)."""
        return await self.model.aembed_documents(texts=text)

    async def get_query_embedding(self, text: str) -> list[float]:
        """Genera un vector embedding para una consulta de búsqueda."""
        return await self.model.aembed_query(text=text)

    def format_database(
        self,
        text_chunks: list[dict],
        vector_chunks: list[list[float]],
        content_type: str = "general"
    ) -> list[dict]:
        """
        Formatea los chunks de texto y sus embeddings para insertar en la colección de Milvus.
        Asigna el tipo de contenido y metadatos asociados.
        """
        formatted_data = []

        for doc, vector in zip(text_chunks, vector_chunks):
            data = {
                "text": doc['text'],
                "vector": vector,
                "source_file": doc.get('metadata', {}).get('source_file', ''),
                "content_type": content_type or "general",
                "metadata": doc.get('metadata', {})
            }
            formatted_data.append(data)

        return formatted_data
