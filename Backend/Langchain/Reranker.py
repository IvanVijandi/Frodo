import os
import logging
from typing import List, Dict, Any, Optional

try:
    from config import conf
except ModuleNotFoundError:
    from Backend.config import conf

logger = logging.getLogger("frodo.reranker")

def extract_hit_text(hit: Any) -> str:
    """
    Extrae de manera resiliente el texto de un resultado de Milvus.
    Soporta diccionarios anidados con 'entity', atributos de objetos Hit,
    y variaciones de nombres de campo ('text', 'text_chunk').
    """
    if isinstance(hit, dict):
        entity = hit.get("entity", {})
        if isinstance(entity, dict):
            text = entity.get("text") or entity.get("text_chunk")
            if text:
                return text
        elif entity is not None:
            text = getattr(entity, "text", None) or getattr(entity, "text_chunk", None)
            if text:
                return text
        return hit.get("text") or hit.get("text_chunk") or ""
    else:
        entity = getattr(hit, "entity", None)
        if entity is not None:
            if isinstance(entity, dict):
                text = entity.get("text") or entity.get("text_chunk")
                if text:
                    return text
            else:
                text = getattr(entity, "text", None) or getattr(entity, "text_chunk", None)
                if text:
                    return text
        return getattr(hit, "text", "") or getattr(hit, "text_chunk", "")


class LocalCrossEncoderReranker:
    """
    Reranker local y soberano basado en CrossEncoder (sentence-transformers).
    Utiliza por defecto el modelo ligero 'cross-encoder/mmarco-mMiniLMv2-L12-H384-v1' (~440 MB).
    """

    def __init__(self, model_name: Optional[str] = None, device: Optional[str] = None):
        self.model_name = model_name or conf.RERANKER_MODEL or "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"
        self.device = device or conf.RERANKER_DEVICE or self._detect_device()

        logger.info(
            f"Inicializando modelo de reranking local '{self.model_name}' en dispositivo '{self.device}'..."
        )

        try:
            from sentence_transformers import CrossEncoder
            self.model = CrossEncoder(self.model_name, device=self.device)
            logger.info(f"Modelo de reranking local '{self.model_name}' cargado exitosamente.")
        except Exception as e:
            logger.error(
                f"Error al cargar el modelo de reranking local '{self.model_name}': {e}. "
                "El sistema continuará con degradación suave (sin rerank)."
            )
            self.model = None

    def _detect_device(self) -> str:
        try:
            import torch
            if torch.cuda.is_available():
                return "cuda"
            if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                return "mps"
        except Exception:
            pass
        return "cpu"

    def rerank(self, query: str, documents: List[Any], top_k: Optional[int] = None) -> List[Any]:
        """
        Reordena la lista de documentos devueltos por Milvus calculando
        el score cruzado (query, texto) con el CrossEncoder.
        """
        if not documents:
            return []

        limit = top_k if top_k is not None else conf.RERANKER_TOP_K

        # Si el modelo no pudo inicializarse, devolver recorte de hits originales
        if self.model is None:
            return documents[:limit]

        pairs = []
        valid_hits = []
        for hit in documents:
            text = extract_hit_text(hit)
            if text and text.strip():
                pairs.append((query, text))
                valid_hits.append(hit)

        if not pairs:
            return documents[:limit]

        try:
            # Inferencia del Cross-Encoder
            scores = self.model.predict(pairs)

            scored_hits = []
            for hit, score in zip(valid_hits, scores):
                float_score = float(score)
                # Inyectar el puntaje en metadatos para trazabilidad y auditoría
                if isinstance(hit, dict):
                    meta = hit.setdefault("metadata", {})
                    if isinstance(meta, dict):
                        meta["rerank_score"] = float_score
                elif hasattr(hit, "entity") and isinstance(hit.entity, dict):
                    hit.entity.setdefault("metadata", {})
                    if isinstance(hit.entity["metadata"], dict):
                        hit.entity["metadata"]["rerank_score"] = float_score

                scored_hits.append((float_score, hit))

            # Ordenar por score de mayor a menor
            scored_hits.sort(key=lambda x: x[0], reverse=True)
            return [hit for _, hit in scored_hits[:limit]]

        except Exception as e:
            logger.error(f"Excepción durante el reranking local: {e}. Retornando resultados originales.")
            return documents[:limit]


class VoyageAIReranker:
    """Proveedor alternativo de reranking en la nube mediante Voyage AI."""

    def __init__(self, api_key: Optional[str] = None):
        import voyageai
        key = api_key or os.getenv("VOYAGE_API_KEY") or conf.VOYAGE_API_KEY
        self.client = voyageai.Client(api_key=key)

    def rerank(self, query: str, documents: List[Any], top_k: Optional[int] = None) -> List[Any]:
        if not documents:
            return []

        limit = top_k if top_k is not None else conf.RERANKER_TOP_K
        lista_chunks = [extract_hit_text(hit) for hit in documents]

        try:
            response = self.client.rerank(
                model="rerank-2",
                query=query,
                documents=lista_chunks,
                top_k=min(limit, len(documents))
            )
            return [documents[r.index] for r in response.results]
        except Exception as e:
            logger.error(f"Error en VoyageAI rerank: {e}. Retornando hits originales.")
            return documents[:limit]


def get_configured_reranker() -> Optional[Any]:
    """Fábrica para instanciar el reranker configurado en variables de entorno."""
    provider = (conf.RERANKER_PROVIDER or "none").lower()

    if provider == "local":
        return LocalCrossEncoderReranker(
            model_name=conf.RERANKER_MODEL,
            device=conf.RERANKER_DEVICE
        )
    elif provider == "voyageai":
        return VoyageAIReranker()
    elif provider in ("none", "false", ""):
        return None
    else:
        logger.warning(f"Proveedor de reranker '{provider}' desconocido. Operando sin reranker.")
        return None


# Alias para mantener compatibilidad con código existente
Reranker = get_configured_reranker
