from typing import TypedDict, Literal, Optional
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from config import conf

# Definición del estado del grafo
class State(TypedDict):
    query: str
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
        
        # Generador: LLM Gemini 
        self.generator_llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            api_key=conf.GEMINI_API_KEY
        )
        
        # Evaluador: LLM Gemini
        self.evaluator_llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", 
            api_key=conf.GEMINI_API_KEY
        ).with_structured_output(Feedback)
        
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
        
        # En la primera iteración realizamos la búsqueda en Milvus
        if iteration == 0:
            query_vector = await self.embedding_generator.get_query_embedding(query)
            results = await self.milvus_client.get_document(
                query_vector=query_vector,
                collection_name="documentos"
            )
            
            if self.reranker and len(results) > 0:
                final_results = self.reranker.rerank(query, results)
            else:
                final_results = results
                
            # Combinar todos los chunks en un solo texto de contexto
            context = "\n\n".join([hit['entity']['text_chunk'] for hit in final_results])
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
            # Máximo 2 intentos (0 y 1). Al llegar a 2 iteraciones cortamos.
            return "Max Iterations Reached"
        else:
            return "Rejected + Feedback"

    def fallback_response(self, state: State):
        # Si luego de múltiples intentos el evaluador no aprueba, devolvemos un mensaje seguro.
        return {"response": "No se cuenta con la información necesaria en el contexto para responder la pregunta de forma fiable."}
