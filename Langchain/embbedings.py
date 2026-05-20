from config import conf
from langchain_ollama import OllamaEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_voyageai import VoyageAIEmbeddings


class EmbeddingGenerator:
    def __init__(self):
        provider = conf.EMBEDDING_PROVIDER.lower()

        if provider == "ollama":
            self.model = OllamaEmbeddings(model="embeddinggemma", base_url=conf.OLLAMA_URI)

        elif provider == "openai":
            self.model = OpenAIEmbeddings(api_key=conf.OPENAI_API_KEY)

        elif provider == "voyage":
            self.model = VoyageAIEmbeddings(voyage_api_key=conf.VOYAGE_API_KEY)

        else:
            raise ValueError(f"Proveedor de embeddings no soportado: {provider}")

    async def get_document_embedding(self, text: list[str]) -> list[list[float]]:
        """Genera embeddings para una lista de textos (documentos)"""
        """Un embedding por string en la lista"""
        return await self.model.aembed_documents(texts=text)  ##La dimension depende del modelo

    async def get_query_embedding(self, text: str) -> list[float]:
        return await self.model.aembed_query(text=text)

    ##A chequear
    def format_database(self, text_chunks: list[dict], vector_chunks: list[list[float]], pdf_id: int) -> list[dict]:
        """
        Formatea los chunks de texto y sus embeddings en una lista de diccionarios para insertar en la base de datos.
        """
        formatted_data = []

        for i, j in zip(text_chunks, vector_chunks):
            data = {
                "text_chunk": i['text'],
                "metadata": i['metadata'],
                "vector_chunk": j,
                "pdf_id": pdf_id
            }
            formatted_data.append(data)

        return formatted_data