import os
from dotenv import load_dotenv


load_dotenv()

class Config:

    MILVUS_URI = os.getenv("MILVUS_URI")
    OLLAMA_URI = os.getenv("OLLAMA_URI")

conf = Config()
