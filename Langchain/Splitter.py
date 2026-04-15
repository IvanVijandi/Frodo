from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

##Función para generar chunks de texto

class Splitter:
    
    def __init__ (self):

        self.modelSplitter = RecursiveCharacterTextSplitter( ##Recibe solo objeto del tipo Document
                chunk_size=1500,  # 1500 caracteres por chunk, aprox. seguro para 2,048 tokens del modelo Gemini que usamos en embeddings
                chunk_overlap=200,  
                add_start_index=True,  
                separators=["\n\n", "\n", ". ", "? ", "! ", " ", ""] ##Crea un nuevo chunk en el primer separador que encuentre
            )
    
    def split_document(self,file_path:str) -> list[dict] :
        """Divide un texto en Document, donde cada uno es una pagina del pdf. Luego divide cada Document en chunks de texto más pequeños.
            Retorna una lista de documentos (chunks)
        """
        
        if file_path:
            loader = PyPDFLoader(file_path)
            docs = loader.load() ##Crea un documento por pagina del PDF
        

        
        all_splits = self.modelSplitter.split_documents(docs) ##Versione futuras, se podría tokenizar el texto !
        
        result = []
        
        for i in all_splits:
            dict = {'text': i.page_content, 'metadata': i.metadata}
            result.append(dict)
        
        return result