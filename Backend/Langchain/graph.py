from typing import TypedDict, Literal, Optional
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI

try:
    from config import conf
except ModuleNotFoundError:
    from Backend.config import conf

# Definición del estado del grafo
class State(TypedDict):
    query: str
    bucket_name: Optional[str]
    context: str
    response: str
    feedback: str
    eval_status: str
    iteration: int

# Esquema para la evaluación estructurada
class Feedback(BaseModel):
    grade: Literal["accepted", "rejected"] = Field(
        description="Decide si la respuesta generada responde a la pregunta original basándose ÚNICAMENTE en el contexto proporcionado.",
    )
    feedback: str = Field(
        description="Si la respuesta es 'rejected', provee feedback específico sobre qué está mal o qué alucinó para que el generador lo corrija. Si es 'accepted', puedes dejarlo vacío.",
    )

class EvaluatorGraph:
    def __init__(self, milvus_client, embedding_generator, reranker):
        self.milvus_client = milvus_client
        self.embedding_generator = embedding_generator
        self.reranker = reranker
        
        provider = conf.LLM_PROVIDER.lower()
        if provider == "ollama":
            evaluator_model = conf.EVALUATOR_MODEL or conf.LLM_MODEL
            # Generador: Ollama
            self.generator_llm = ChatOllama(
                base_url=conf.OLLAMA_URI,
                model=conf.LLM_MODEL,
                temperature=0.2,
                reasoning=False
            )
            # Evaluador: Ollama
            self.evaluator_llm = ChatOllama(
                base_url=conf.OLLAMA_URI,
                model=evaluator_model,
                temperature=0.0,
                reasoning=False
            ).with_structured_output(Feedback)
        elif provider == "google":
            evaluator_model = conf.EVALUATOR_MODEL or "gemini-2.5-flash"
            # Generador: LLM Gemini 
            self.generator_llm = ChatGoogleGenerativeAI(
                model=conf.LLM_MODEL or "gemini-2.5-flash-lite",
                api_key=conf.GEMINI_API_KEY
            )
            # Evaluador: LLM Gemini
            self.evaluator_llm = ChatGoogleGenerativeAI(
                model=evaluator_model, 
                api_key=conf.GEMINI_API_KEY
            ).with_structured_output(Feedback)
        else:
            raise ValueError(f"Proveedor de LLM '{provider}' no soportado.")
        
        # Constructor del Grafo
        builder = StateGraph(State)
        
        builder.add_node("retrieve_and_generate", self.retrieve_and_generate)
        builder.add_node("evaluate", self.evaluate)
        builder.add_node("fallback_response", self.fallback_response)
        
        builder.add_edge(START, "retrieve_and_generate")
        builder.add_edge("retrieve_and_generate", "evaluate")
        builder.add_conditional_edges(
            "evaluate",
            self.route_evaluation,
            {
                "Accepted": END,
                "Rejected + Feedback": "retrieve_and_generate",
                "Max Iterations Reached": "fallback_response"
            }
        )
        builder.add_edge("fallback_response", END)
        
        self.graph = builder.compile()

    async def retrieve_and_generate(self, state: State):
        query = state["query"]
        iteration = state.get("iteration", 0)
        bucket = state.get("bucket_name") or "general"
        
        # En la primera iteración realizamos la búsqueda en Milvus en el bucket especificado
        if iteration == 0:
            query_vector = await self.embedding_generator.get_query_embedding(query)
            results = await self.milvus_client.get_document(
                query_vector=query_vector,
                collection_name=bucket
            )
            
            # Asegurar lista plana de hits (desempaquetar si viene anidado)
            hits = results[0] if (results and isinstance(results, list) and len(results) > 0 and isinstance(results[0], list)) else (results or [])
            
            if self.reranker and len(hits) > 0:
                final_results = self.reranker.rerank(query, hits)
            else:
                final_results = hits
                
            # Combinar todos los chunks en un solo texto de contexto
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
            print(f"[RAG] Bucket: '{bucket}' | Hits recuperados: {len(hits)} | Chunks con texto: {len(context_chunks)}")
        else:
            # En iteraciones posteriores usamos el contexto que ya buscamos
            context = state["context"]
            
        feedback = state.get("feedback", "")
        
        # Prompt para el generador asegurando que se ciña al contexto
        prompt = f"""Eres un asistente útil. Debes responder a la PREGUNTA utilizando ÚNICAMENTE la información proporcionada en el CONTEXTO.
    Si el contexto no contiene información suficiente para responder, no inventes nada; debes indicar que no cuentas con la información.

    PREGUNTA: {query}

    CONTEXTO:
    {context}
    """
        if feedback:
            prompt += f"\n\nATENCIÓN: Tu respuesta anterior fue evaluada y RECHAZADA por el siguiente motivo: '{feedback}'.\nPor favor, corrige tu respuesta asegurándote de basarte SOLO en el contexto."
            
        msg = await self.generator_llm.ainvoke(prompt)
        
        return {"response": msg.content, "context": context}

    async def evaluate(self, state: State):
        query = state["query"]
        context = state["context"]
        response = state["response"]
        iteration = state.get("iteration", 0)
        
        prompt = f"""Eres un juez estricto. Tu tarea es evaluar si la RESPUESTA responde adecuadamente a la PREGUNTA basándose EXCLUSIVAMENTE en el CONTEXTO proporcionado.
Es de vital importancia que la respuesta no contenga información inventada (alucinaciones) que no se encuentre explícitamente en el contexto. Si no se puede responder con el contexto y el asistente dice que no sabe, está bien (eso es 'accepted'). Pero si intenta responder inventando, es 'rejected'.

PREGUNTA: {query}

CONTEXTO:
{context}

RESPUESTA A EVALUAR:
{response}
"""
        grade = await self.evaluator_llm.ainvoke(prompt)
        
        return {
            "eval_status": grade.grade, 
            "feedback": grade.feedback,
            "iteration": iteration + 1
        }
        
    def route_evaluation(self, state: State):
        if state["eval_status"] == "accepted":
            return "Accepted"
        elif state["iteration"] >= 2:
            return "Max Iterations Reached"
        else:
            return "Rejected + Feedback"

    def fallback_response(self, state: State):
        return {"response": "No se cuenta con la información necesaria en el contexto para responder la pregunta de forma fiable."}
