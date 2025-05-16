from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain.embeddings import OllamaEmbeddings
from langchain.vectorstores import FAISS
import os

class DocumentProcessor:
    def __init__(self):
        self.embeddings = OllamaEmbeddings(model="deepseek-coder-v2:16b")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
        # Create vectors directory if it doesn't exist
        if not os.path.exists('vectors'):
            os.makedirs('vectors')

    def process_document(self, file_path, file_type):
        """Process document and return extracted text and vector store path"""
        if file_type == 'pdf':
            loader = PyPDFLoader(file_path)
        elif file_type == 'docx':
            loader = Docx2txtLoader(file_path)
        elif file_type == 'txt':
            loader = TextLoader(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

        documents = loader.load()
        texts = self.text_splitter.split_documents(documents)
        
        # Create vector store
        vector_store_path = f"vectors/{os.path.basename(file_path)}_store"
        vector_store = FAISS.from_documents(texts, self.embeddings)
        vector_store.save_local(vector_store_path)
        
        # Return the full text and vector store path
        return "\n".join([doc.page_content for doc in documents]), vector_store_path

    def query_document(self, vector_store_path, query):
        """Query the document using the vector store"""
        vector_store = FAISS.load_local(vector_store_path, self.embeddings)
        docs = vector_store.similarity_search(query)
        return [doc.page_content for doc in docs]