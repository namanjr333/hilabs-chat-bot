from langchain_ollama.llms import OllamaLLM
from langchain_community.document_loaders import PDFPlumberLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores.faiss import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
import faiss

llm = OllamaLLM(model ="llama3.1")
embeddings = OllamaEmbeddings(model="llama3.1")

def get_documents(file_path):
    loader = PDFPlumberLoader(file_path)
    content = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=10)
    docs = text_splitter.split_documents(content)
    return docs

def create_vector_store():
    index = faiss.IndexFlatL2(len(embeddings.embed_query("hello world")))
    vector_store = FAISS(
        embedding_function=embeddings,
        index=index,
        docstore= InMemoryDocstore(),
        index_to_docstore_id={}
    )
    return vector_store

def add_documents_to_vector_store(vector_store: FAISS, docs):
    vector_store.add_documents(documents=docs)
    
def get_answer(vector_store, question):
    results = vector_store.similarity_search(query=question, k=10000)
    context_str = ""
    for doc in results:
        context_str += doc.page_content
        context_str += " "
    response = llm.invoke("The document is about " + context_str + " and the user is asking questions about " + question)
    return response


if __name__ == '__main__':
    print("Starting")

    question = "What is the document about?"

    vector_store = create_vector_store()
    print("Vector Store Created")

    docs = get_documents("Samples/Contract 1.pdf")
    print("Documents Loaded", len(docs))

    add_documents_to_vector_store(vector_store, docs)
    print("Documents Added to Vector Store")

    response = get_answer(vector_store, question)
    print(response)