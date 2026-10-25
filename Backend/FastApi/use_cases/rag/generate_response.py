import json
from typing import Dict, Any, Optional, AsyncGenerator

try:
    from Langchain.graph import EvaluatorGraph
except ModuleNotFoundError:
    from Backend.Langchain.graph import EvaluatorGraph

class GenerateResponseUseCase:
    """Caso de uso para generar respuestas RAG contextualizadas, evaluadas y con soporte de streaming SSE."""

    def __init__(self, milvus_client, embedding_generator, reranker: Optional[Any] = None):
        self.milvus_client = milvus_client
        self.embedding_generator = embedding_generator
        self.reranker = reranker

    def _create_evaluator_graph(self) -> EvaluatorGraph:
        return EvaluatorGraph(
            milvus_client=self.milvus_client,
            embedding_generator=self.embedding_generator,
            reranker=self.reranker
        )

    async def execute_stream(self, query: str, bucket_name: str = "general") -> AsyncGenerator[str, None]:
        target_bucket = bucket_name.strip() if bucket_name else "general"

        if not await self.milvus_client.bucket_exists(target_bucket):
            yield f"data: {json.dumps({'error': f'El bucket {target_bucket} no existe.', 'done': True})}\n\n"
            return

        evaluator_graph = self._create_evaluator_graph()

        try:
            # 1. Recuperar contexto vectorial desde Milvus
            query_vector = await self.embedding_generator.get_query_embedding(query)
            results = await self.milvus_client.get_document(
                query_vector=query_vector,
                collection_name=target_bucket
            )

            hits = results[0] if (results and isinstance(results, list) and len(results) > 0 and isinstance(results[0], list)) else (results or [])
            if self.reranker and len(hits) > 0:
                final_results = self.reranker.rerank(query, hits)
            else:
                final_results = hits

            context_chunks = []
            for hit in final_results:
                text = ""
                if isinstance(hit, dict):
                    entity = hit.get('entity', {})
                    if isinstance(entity, dict):
                        text = entity.get('text') or entity.get('text_chunk') or ""
                    text = text or hit.get('text') or hit.get('text_chunk') or ""
                else:
                    entity = getattr(hit, 'entity', None)
                    if entity:
                        text = getattr(entity, 'text', '') or getattr(entity, 'text_chunk', '')
                    text = text or getattr(hit, 'text', '') or getattr(hit, 'text_chunk', '')
                if text:
                    context_chunks.append(text)

            context = "\n\n".join(context_chunks)

            # 2. Construir prompt contextual
            if not context.strip():
                prompt = f"""Eres un asistente útil de MARIA. El usuario hizo la siguiente pregunta:
"{query}"

Sin embargo, en el bucket '{target_bucket}' no se encontró contexto ni fragmentos relacionados en los documentos.
Explica cortésmente que en los documentos indexados en el bucket '{target_bucket}' no se cuenta con información suficiente para responder, e invita al usuario a verificar los documentos o subir el archivo PDF correspondiente.
"""
            else:
                prompt = f"""Eres un asistente útil. Debes responder a la PREGUNTA utilizando ÚNICAMENTE la información proporcionada en el CONTEXTO.
Si el contexto no contiene información suficiente para responder, no inventes nada; debes indicar claramente que no cuentas con la información suficiente en los documentos para responder.

PREGUNTA: {query}

CONTEXTO:
{context}
"""

            # 3. Transmitir tokens en vivo de Ollama
            accumulated = ""
            async for chunk in evaluator_graph.generator_llm.astream(prompt):
                content = chunk.content if hasattr(chunk, 'content') else str(chunk)
                if content:
                    accumulated += content
                    yield f"data: {json.dumps({'token': content, 'done': False})}\n\n"

            # 4. Finalizar stream con evento final
            yield f"data: {json.dumps({'token': '', 'done': True, 'response': accumulated, 'bucket': target_bucket})}\n\n"

        except Exception as stream_err:
            yield f"data: {json.dumps({'error': str(stream_err), 'done': True})}\n\n"

    async def execute_evaluated(self, query: str, bucket_name: str = "general") -> Dict[str, Any]:
        target_bucket = bucket_name.strip() if bucket_name else "general"

        if not await self.milvus_client.bucket_exists(target_bucket):
            raise KeyError(f"El bucket '{target_bucket}' no existe.")

        evaluator_graph = self._create_evaluator_graph()

        initial_state = {
            "query": query,
            "bucket_name": target_bucket,
            "context": "",
            "response": "",
            "feedback": "",
            "eval_status": "",
            "iteration": 0
        }

        final_state = await evaluator_graph.graph.ainvoke(initial_state)

        return {
            "message": "Respuesta evaluada y aprobada por el juez." if final_state["eval_status"] == "accepted" else "Límite de iteraciones alcanzado o sin contexto suficiente.",
            "bucket": target_bucket,
            "response": final_state["response"],
            "iteration": final_state.get("iteration", 0)
        }

