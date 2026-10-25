import json
import uuid
from typing import Dict, Any, Optional, AsyncGenerator

try:
    from Langchain.graph import EvaluatorGraph
    from config import conf
except ModuleNotFoundError:
    from Backend.Langchain.graph import EvaluatorGraph
    from Backend.config import conf

class GenerateResponseUseCase:
    """Caso de uso para generar respuestas RAG contextualizadas, evaluadas y con persistencia en PostgreSQL."""

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

    async def execute_stream(
        self,
        query: str,
        bucket_name: str = "general",
        conversacion_id: Optional[str] = None,
        db: Optional[Any] = None
    ) -> AsyncGenerator[str, None]:
        target_bucket = bucket_name.strip() if bucket_name else "general"

        if not await self.milvus_client.bucket_exists(target_bucket):
            yield f"data: {json.dumps({'error': f'El bucket {target_bucket} no existe.', 'done': True})}\n\n"
            return

        # 0. Gestionar o recuperar conversación y persistir mensaje del usuario en PostgreSQL
        target_conv = None
        if db:
            try:
                from Postgres import repository
                pg_bucket = await repository.get_or_create_bucket(db, target_bucket)

                if conversacion_id:
                    try:
                        c_uuid = uuid.UUID(str(conversacion_id))
                        target_conv = await repository.get_conversacion(db, c_uuid, include_mensajes=False)
                    except (ValueError, TypeError):
                        pass

                if not target_conv:
                    title = query[:40].strip() + ("..." if len(query) > 40 else "")
                    target_conv = await repository.create_conversacion(
                        db=db,
                        bucket_id=pg_bucket.id,
                        title=title or "Nueva conversación"
                    )

                await repository.add_mensaje(
                    db=db,
                    conversacion_id=target_conv.id,
                    role="user",
                    content=query
                )
            except Exception as e:
                print(f"Nota al registrar mensaje de usuario en PostgreSQL: {e}")

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
            clean_sources = []
            for hit in final_results:
                text = ""
                src_file = "desconocido"
                score_val = None

                if isinstance(hit, dict):
                    entity = hit.get('entity', {})
                    if isinstance(entity, dict):
                        text = entity.get('text') or entity.get('text_chunk') or ""
                        src_file = entity.get('source_file', src_file)
                    text = text or hit.get('text') or hit.get('text_chunk') or ""
                    src_file = hit.get('source_file') or src_file
                    score_val = hit.get('distance') or hit.get('score')
                else:
                    entity = getattr(hit, 'entity', None)
                    if entity:
                        text = getattr(entity, 'text', '') or getattr(entity, 'text_chunk', '')
                        src_file = getattr(entity, 'source_file', src_file)
                    text = text or getattr(hit, 'text', '') or getattr(hit, 'text_chunk', '')
                    src_file = getattr(hit, 'source_file', src_file)
                    score_val = getattr(hit, 'distance', None) or getattr(hit, 'score', None)

                if text:
                    context_chunks.append(text)
                    clean_sources.append({
                        "source": src_file,
                        "score": round(float(score_val), 4) if score_val is not None else None
                    })

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

            # 4. Persistir respuesta del asistente en PostgreSQL
            if db and target_conv:
                try:
                    from Postgres import repository
                    await repository.add_mensaje(
                        db=db,
                        conversacion_id=target_conv.id,
                        role="assistant",
                        content=accumulated,
                        sources=clean_sources[:5],
                        extra_metadata={"model": getattr(conf, "LLM_MODEL", "qwen3.5:4b")}
                    )
                except Exception as e:
                    print(f"Nota al registrar mensaje de asistente en PostgreSQL: {e}")

            # 5. Finalizar stream con evento final
            yield f"data: {json.dumps({'token': '', 'done': True, 'response': accumulated, 'bucket': target_bucket, 'conversacion_id': str(target_conv.id) if target_conv else None})}\n\n"

        except Exception as stream_err:
            yield f"data: {json.dumps({'error': str(stream_err), 'done': True})}\n\n"

    async def execute_evaluated(
        self,
        query: str,
        bucket_name: str = "general",
        conversacion_id: Optional[str] = None,
        db: Optional[Any] = None
    ) -> Dict[str, Any]:
        target_bucket = bucket_name.strip() if bucket_name else "general"

        if not await self.milvus_client.bucket_exists(target_bucket):
            raise KeyError(f"El bucket '{target_bucket}' no existe.")

        target_conv = None
        if db:
            try:
                from Postgres import repository
                pg_bucket = await repository.get_or_create_bucket(db, target_bucket)

                if conversacion_id:
                    try:
                        c_uuid = uuid.UUID(str(conversacion_id))
                        target_conv = await repository.get_conversacion(db, c_uuid, include_mensajes=False)
                    except (ValueError, TypeError):
                        pass

                if not target_conv:
                    title = query[:40].strip() + ("..." if len(query) > 40 else "")
                    target_conv = await repository.create_conversacion(
                        db=db,
                        bucket_id=pg_bucket.id,
                        title=title or "Nueva conversación"
                    )

                await repository.add_mensaje(
                    db=db,
                    conversacion_id=target_conv.id,
                    role="user",
                    content=query
                )
            except Exception as e:
                print(f"Nota al registrar mensaje de usuario en PostgreSQL: {e}")

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

        if db and target_conv:
            try:
                from Postgres import repository
                await repository.add_mensaje(
                    db=db,
                    conversacion_id=target_conv.id,
                    role="assistant",
                    content=final_state["response"],
                    sources=[],
                    extra_metadata={
                        "model": getattr(conf, "LLM_MODEL", "qwen3.5:4b"),
                        "eval_status": final_state.get("eval_status"),
                        "iteration": final_state.get("iteration", 0)
                    }
                )
            except Exception as e:
                print(f"Nota al registrar mensaje evaluado en PostgreSQL: {e}")

        return {
            "message": "Respuesta evaluada y aprobada por el juez." if final_state["eval_status"] == "accepted" else "Límite de iteraciones alcanzado o sin contexto suficiente.",
            "bucket": target_bucket,
            "response": final_state["response"],
            "iteration": final_state.get("iteration", 0),
            "conversacion_id": str(target_conv.id) if target_conv else None
        }
