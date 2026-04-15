from fastapi import FastAPI
from contextlib import asynccontextmanager
from Langchain.embbedings import EmbeddingGenerator
from Langchain.Reranker import Reranker 


##Lifespan. Se encarga de inicializar y cerrar recursos al iniciar y cerrar el servidor.
@asynccontextmanager
async def lifespan(app: FastAPI):
    ##Instancias de las clases
    reranker = Reranker()
    embedding_generator = EmbeddingGenerator()
    
    

app = FastAPI(llifespan=lifespan)

##Para probar que el servidor esta corriendo
@app.get("/")
async def ok():
    return {"message": "ok"}



@app.post("/uploadFile")
async def upload_file():
    return None

