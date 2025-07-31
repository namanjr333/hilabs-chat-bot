from langchain_ollama.llms import OllamaLLM
from langchain_community.document_loaders import PDFPlumberLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_community.vectorstores.faiss import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
import faiss
import logging
from typing import List, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize models with error handling
try:
    llm = OllamaLLM(model="llama3.1")
    embeddings = OllamaEmbeddings(model="llama3.1")
    logger.info("Successfully initialized Ollama models")
except Exception as e:
    logger.error(f"Failed to initialize Ollama models: {e}")
    raise

def get_documents(file_path: str) -> List:
    """
    Extract and split documents from PDF file.
    
    Args:
        file_path (str): Path to the PDF file
        
    Returns:
        List: List of document chunks
    """
    try:
        logger.info(f"Loading document from: {file_path}")
        loader = PDFPlumberLoader(file_path)
        content = loader.load()
        
        # Optimized chunk size for better context retention
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,  # Increased from 100 for better context
            chunk_overlap=100,  # Increased overlap for better continuity
            separators=["\n\n", "\n", ". ", " ", ""]  # Better splitting strategy
        )
        docs = text_splitter.split_documents(content)
        
        logger.info(f"Successfully split document into {len(docs)} chunks")
        return docs
        
    except Exception as e:
        logger.error(f"Error processing document {file_path}: {e}")
        raise

def create_vector_store() -> FAISS:
    """
    Create a new FAISS vector store.
    
    Returns:
        FAISS: Empty vector store
    """
    try:
        # Get embedding dimension
        sample_embedding = embeddings.embed_query("sample text")
        embedding_dim = len(sample_embedding)
        
        index = faiss.IndexFlatL2(embedding_dim)
        vector_store = FAISS(
            embedding_function=embeddings,
            index=index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={}
        )
        
        logger.info(f"Created vector store with embedding dimension: {embedding_dim}")
        return vector_store
        
    except Exception as e:
        logger.error(f"Error creating vector store: {e}")
        raise

def add_documents_to_vector_store(vector_store: FAISS, docs: List) -> None:
    """
    Add documents to the vector store.
    
    Args:
        vector_store (FAISS): The vector store to add documents to
        docs (List): List of documents to add
    """
    try:
        if not docs:
            logger.warning("No documents to add to vector store")
            return
            
        vector_store.add_documents(documents=docs)
        logger.info(f"Added {len(docs)} documents to vector store")
        
    except Exception as e:
        logger.error(f"Error adding documents to vector store: {e}")
        raise

def get_answer(vector_store: FAISS, question: str, k: int = 5) -> str:
    """
    Get answer to a question using the vector store and LLM.
    
    Args:
        vector_store (FAISS): The vector store to search
        question (str): The user's question
        k (int): Number of documents to retrieve (default: 5)
        
    Returns:
        str: The LLM's response
    """
    try:
        if not question.strip():
            return "Please provide a valid question."
        
        # Optimized similarity search - reduced from 10000 to reasonable number
        logger.info(f"Searching for relevant documents for question: {question[:50]}...")
        results = vector_store.similarity_search(query=question, k=k)
        
        if not results:
            return "I couldn't find any relevant information in the document to answer your question."
        
        # Build context from retrieved documents
        context_parts = []
        for i, doc in enumerate(results):
            context_parts.append(f"[Context {i+1}]: {doc.page_content.strip()}")
        
        context_str = "\n\n".join(context_parts)
        
        # Improved prompt for better responses
        prompt = f"""Based on the following document excerpts, please answer the user's question. If the information is not available in the provided context, please say so.

Context:
{context_str}

Question: {question}

Please provide a clear, concise answer based only on the information provided in the context above."""

        logger.info("Generating response with LLM")
        response = llm.invoke(prompt)
        
        return response.strip()
        
    except Exception as e:
        logger.error(f"Error generating answer: {e}")
        return "I'm sorry, I encountered an error while processing your question. Please try again."

def test_system() -> bool:
    """
    Test if the system components are working correctly.
    
    Returns:
        bool: True if all components are working
    """
    try:
        # Test LLM
        test_response = llm.invoke("Hello, can you respond?")
        if not test_response:
            return False
            
        # Test embeddings
        test_embedding = embeddings.embed_query("test")
        if not test_embedding:
            return False
            
        logger.info("System test passed")
        return True
        
    except Exception as e:
        logger.error(f"System test failed: {e}")
        return False

if __name__ == '__main__':
    print("Starting RAG System Test...")
    
    # Test system components
    if not test_system():
        print("System test failed. Please check Ollama installation.")
        exit(1)
    
    question = "What is the document about?"

    try:
        vector_store = create_vector_store()
        print("Vector Store Created")

        docs = get_documents("Samples/Contract 1.pdf")
        print(f"Documents Loaded: {len(docs)} chunks")

        add_documents_to_vector_store(vector_store, docs)
        print("Documents Added to Vector Store")

        response = get_answer(vector_store, question)
        print(f"\nQuestion: {question}")
        print(f"Answer: {response}")
        
    except Exception as e:
        print(f"Error: {e}")
        exit(1)