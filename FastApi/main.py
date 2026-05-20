from fastapi import FastAPI, UploadFile, HTTPException, File, Depends, Request
from contextlib import asynccontextmanager
from Langchain.embbedings import EmbeddingGenerator
from Langchain.Reranker import Reranker 
from Milvus.main import Async_Milvus_Client
from Langchain.pdf_service import process_pdf_upload

##Lifespan. Se encarga de inicializar y cerrar recursos al iniciar y cerrar el servidor.
@asynccontextmanager
async def lifespan(app: FastAPI):
    ##Instancias de las clases pesadas guardadas en app.state
    app.state.reranker = Reranker()
    app.state.embedding_generator = EmbeddingGenerator()
    app.state.milvus_client = Async_Milvus_Client()
    yield

app = FastAPI(lifespan=lifespan)

# Dependencias para inyectar en los endpoints
def get_milvus_client(request: Request):
    return request.app.state.milvus_client

def get_embedding_generator(request: Request):
    return request.app.state.embedding_generator

##Para probar que el servidor esta corriendo
@app.get("/")
async def ok():
    return {"message": "ok"}

@app.post("/upload-file")
async def upload_file(
    file: UploadFile = File(...),
    milvus_client: Async_Milvus_Client = Depends(get_milvus_client),
    embedding_generator: EmbeddingGenerator = Depends(get_embedding_generator)
):
    if not file.filename.lower().endswith(".pdf") or file.content_type != "application/pdf":
        raise HTTPException(status_code=415, detail="Solo se admiten archivos PDF.")
    
    try:
        # 1. Procesar PDF (guardar temp, extraer, split)
        docs = await process_pdf_upload(file)
        if not docs:
            return {"message": "El documento PDF está vacío o no se pudo extraer texto."}

        # docs ya es una lista de diccionarios con 'text' y 'metadata'
        text_chunks = [doc['text'] for doc in docs]

        # 2. Generar embeddings
        vector_chunks = await embedding_generator.get_document_embedding(text_chunks)

        # 3. Formatear para Milvus
        # Usamos un pdf_id ficticio o generado. Idealmente vendría de una tabla en DB relacional.
        import time
        pdf_id = int(time.time())

        # El método format_database espera text_chunks como list[dict] con 'text' y 'metadata'
        # ¡docs ya tiene este formato exacto!
        data_to_insert = embedding_generator.format_database(docs, vector_chunks, pdf_id)

        # 4. Insertar en Milvus
        await milvus_client.upload_document(data=data_to_insert, collection_name="documentos")

        return {
            "message": "Archivo cargado y procesado con éxito.",
            "chunks_procesados": len(docs),
            "pdf_id": pdf_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

