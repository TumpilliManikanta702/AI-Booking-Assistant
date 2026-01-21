import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

class RAGPipeline:
    def __init__(self, vector_store_path="faiss_index"):
        self.vector_store_path = vector_store_path
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2", model_kwargs={'device': 'cpu'})
        self.vector_store = None
        self.load_vector_store()

    def process_pdfs(self, pdf_files):
        """
        Process a list of uploaded PDF files.
        pdf_files: List of uploaded file objects (Streamlit UploadedFile)
        """
        documents = []
        for pdf_file in pdf_files:
            # Save temp file to read
            with open(f"temp_{pdf_file.name}", "wb") as f:
                f.write(pdf_file.getbuffer())
            
            loader = PyPDFLoader(f"temp_{pdf_file.name}")
            docs = loader.load()
            documents.extend(docs)
            
            # Clean up temp file
            os.remove(f"temp_{pdf_file.name}")
        
        if not documents:
            return "No documents processed."

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(documents)
        
        self.vector_store = FAISS.from_documents(chunks, self.embeddings)
        self.vector_store.save_local(self.vector_store_path)
        return f"Processed {len(documents)} pages into {len(chunks)} chunks."

    def load_vector_store(self):
        if os.path.exists(self.vector_store_path):
            try:
                self.vector_store = FAISS.load_local(
                    self.vector_store_path, 
                    self.embeddings, 
                    allow_dangerous_deserialization=True
                )
            except Exception as e:
                print(f"Error loading vector store: {e}")
                self.vector_store = None

    def query(self, query_text, k=3):
        if not self.vector_store:
            return "Knowledge base is empty. Please upload PDFs first."
        
        docs = self.vector_store.similarity_search(query_text, k=k)
        return "\n\n".join([doc.page_content for doc in docs])
