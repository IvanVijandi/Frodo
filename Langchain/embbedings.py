##Generador de Embeddings
from langchain_ollama import OllamaEmbeddings

##Modelo de embeddings
embed = OllamaEmbeddings(model = "embeddinggemma")

input_text = "The meaning of life is 42"
vector = embed.embed_query(input_text)
print(vector)