# HiLabs Chat Bot - Complete Project Summary

## 📋 Project Overview

**HiLabs Chat Bot** is a locally-hosted, AI-powered PDF document question-answering system that leverages Retrieval-Augmented Generation (RAG) to enable users to ask questions about uploaded PDF documents. The chatbot uses Meta's Llama 3.1 model running through Ollama for both text generation and embeddings, ensuring complete data privacy by processing everything locally.

## 🎯 Purpose and Use Case

The primary purpose of this application is to:
- Enable users to extract information from PDF documents through natural language queries
- Provide an intelligent document analysis tool that runs entirely on local infrastructure
- Demonstrate practical implementation of RAG architecture with open-source LLMs
- Support contract analysis and document review workflows (as evidenced by sample contract PDFs)

## 🏗️ Architecture

The application follows a classic RAG (Retrieval-Augmented Generation) architecture with five main stages:

### Workflow Pipeline

```
1. PDF Upload → 2. Document Processing → 3. Vector Embedding → 4. Similarity Search → 5. LLM Response
```

#### Detailed Flow:

1. **PDF to Text Conversion**
   - PDFs are uploaded through the web interface
   - PDFPlumber extracts text content from PDF files
   - Documents are split into manageable chunks

2. **Document Chunking**
   - RecursiveCharacterTextSplitter divides text into chunks
   - Chunk size: 100 characters
   - Chunk overlap: 10 characters
   - This ensures context continuity across chunks

3. **Vector Embedding Generation**
   - Each chunk is converted to vector embeddings using Llama 3.1
   - Embeddings capture semantic meaning of text
   - OllamaEmbeddings handles the embedding generation

4. **Vector Database Storage**
   - FAISS (Facebook AI Similarity Search) stores embeddings in-memory
   - Uses IndexFlatL2 for efficient similarity computations
   - Session-based storage allows multiple concurrent users

5. **Question-Answer Process**
   - User submits a question
   - System performs similarity search in vector database (k=10000)
   - Retrieved relevant document chunks provide context
   - Llama 3.1 LLM generates answer based on context + question

## 🛠️ Technology Stack

### Backend Framework
- **Flask**: Web application framework
- **Python**: Primary programming language

### AI/ML Components
- **Llama 3.1**: Large Language Model (via Ollama)
- **LangChain**: Framework for LLM application development
  - langchain_ollama: Ollama integration
  - langchain_community: Community extensions
  - langchain_core: Core functionality
- **FAISS**: Vector similarity search library (CPU version)

### Document Processing
- **PyPDF2 & pypdf**: PDF manipulation
- **PDFPlumber**: Enhanced PDF text extraction
- **BeautifulSoup4**: HTML/XML parsing support

### Additional Libraries
- **sentence_transformers**: Text embedding models
- **chromadb**: Alternative vector database support
- **groq & langchain-groq**: Groq API integration
- **langchain-objectbox**: ObjectBox integration
- **Wikipedia & ArXiv**: External knowledge sources
- **LangChain Hub**: Pre-built chains and prompts

### Development Tools
- **python-dotenv**: Environment variable management
- **FastAPI & uvicorn**: Alternative API framework support
- **Streamlit**: Alternative UI framework support
- **sse_starlette**: Server-Sent Events support

## 📁 Project Structure

```
hilabs-chat-bot/
├── server.py              # Flask web server and API endpoints
├── rag.py                 # RAG logic: embedding, vector store, Q&A
├── requirements.txt       # Python dependencies
├── README.md             # Installation and usage guide
├── test.ipynb            # Jupyter notebook for testing
├── templates/
│   └── index.html        # Web UI (single-page application)
├── Samples/              # Sample PDF files for testing
│   ├── Contract 1.pdf
│   ├── Contract 2.pdf
│   └── ... (15 total contract PDFs)
└── uploads/              # Runtime directory for uploaded files
    └── [session-id]/     # Session-specific upload folders
```

## 🔧 Core Components

### 1. server.py (Flask Application)

**Purpose**: Web server handling HTTP requests and managing user sessions

**Key Features**:
- Session management with UUID-based keys
- File upload handling with secure filenames
- In-memory session storage (db dictionary)
- RESTful API endpoints

**API Endpoints**:
- `GET /` - Serves the web interface
- `GET /get-session-key` - Creates new user session
- `POST /upload-pdf` - Handles PDF file uploads
- `GET /process-pdf` - Processes uploaded PDF into vector store
- `POST /ask-question` - Accepts questions and returns AI-generated answers
- `GET /get-messages` - Retrieves chat history for session

**Session Structure**:
```python
{
    'session_id': {
        'vector_store': FAISS instance,
        'pdf_paths': [list of uploaded PDF paths],
        'mssgs': [list of Q&A pairs]
    }
}
```

### 2. rag.py (RAG Implementation)

**Purpose**: Implements the core RAG functionality

**Key Functions**:

- `get_documents(file_path)`: 
  - Loads PDF using PDFPlumberLoader
  - Splits into chunks (100 chars, 10 overlap)
  - Returns list of document objects

- `create_vector_store()`:
  - Initializes FAISS index with L2 distance
  - Creates in-memory document store
  - Returns empty vector store ready for documents

- `add_documents_to_vector_store(vector_store, docs)`:
  - Embeds documents using Llama 3.1
  - Adds to FAISS index
  - Updates docstore mapping

- `get_answer(vector_store, question)`:
  - Performs similarity search (k=10000)
  - Concatenates retrieved context
  - Constructs prompt for LLM
  - Returns generated answer

**LLM Configuration**:
- Model: llama3.1
- Embeddings: llama3.1
- Temperature/Parameters: Default Ollama settings

### 3. templates/index.html (Web Interface)

**Purpose**: Single-page web application for user interaction

**Features**:
- Session management ("New Session" button)
- PDF file upload with validation
- Processing trigger
- Question input form
- Chat history display
- Loading spinner for async operations
- Responsive design with modern CSS

**User Flow**:
1. Click "New Session" to start
2. Upload PDF file
3. Click "Process PDF" to analyze document
4. Enter questions and submit
5. View answers in chat interface

**JavaScript Functions**:
- `getSessionKey()`: Initializes new session
- `uploadPDF()`: Handles file upload
- `processPDF()`: Triggers document processing
- `askQuestion()`: Submits questions and displays answers
- `showLoading()/hideLoading()`: UI feedback

## 🚀 Setup and Installation

### Prerequisites
1. **Install Ollama**:
   ```bash
   curl -sSL https://ollama.com/install.sh | bash
   ```

2. **Pull Llama 3.1 Model**:
   ```bash
   ollama pull llama3.1
   ```

### Installation Steps

1. **Clone Repository**:
   ```bash
   git clone https://github.com/namanjr333/hilabs-chat-bot.git
   cd hilabs-chat-bot
   ```

2. **Create Virtual Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Start Server**:
   ```bash
   python server.py
   ```

5. **Access Application**:
   - Open browser to: http://localhost:5000

## 💡 Usage Example

### Step-by-Step Usage:

1. **Start New Session**:
   - Click "New Session" button
   - System generates UUID session key
   - Creates isolated vector store for your session

2. **Upload Document**:
   - Click "Choose File" and select a PDF
   - Click "Upload PDF"
   - File saved to `uploads/[session-id]/[filename].pdf`

3. **Process Document**:
   - Click "Process PDF" button
   - System extracts text, creates chunks, generates embeddings
   - Stores vectors in FAISS index (takes 10-30 seconds depending on size)

4. **Ask Questions**:
   - Type question in text field (e.g., "What is this contract about?")
   - Click "Submit Question"
   - System retrieves relevant chunks, generates answer
   - Answer appears in chat history

5. **Continue Conversation**:
   - Ask follow-up questions about the same document
   - All Q&A pairs stored in session history
   - View complete conversation in chat area

## 🎯 Key Features

### 1. **Local Processing**
   - All data stays on your machine
   - No external API calls for LLM inference
   - Complete privacy for sensitive documents

### 2. **Session Management**
   - Multi-user support through UUID sessions
   - Isolated vector stores per session
   - Chat history preservation

### 3. **RAG Architecture**
   - Semantic search for relevant context
   - Reduces hallucination by grounding answers
   - Efficient document retrieval

### 4. **Flexible Document Support**
   - PDF processing with PDFPlumber
   - Handles multi-page documents
   - Chunk-based processing for large files

### 5. **User-Friendly Interface**
   - Clean, modern web UI
   - Real-time feedback with loading indicators
   - Conversational chat interface
   - Alert notifications for operations

## 🔍 Technical Details

### Vector Store Configuration
- **Index Type**: FAISS IndexFlatL2 (exhaustive search)
- **Distance Metric**: L2 (Euclidean distance)
- **Storage**: In-memory (not persisted)
- **Retrieval**: k=10000 (retrieves all chunks effectively)

### Document Processing
- **Chunk Size**: 100 characters
- **Overlap**: 10 characters
- **Reason**: Small chunks for precise retrieval, overlap maintains context

### LLM Prompt Structure
```
"The document is about [CONTEXT] and the user is asking questions about [QUESTION]"
```

### Performance Considerations
- In-memory storage: Fast but not persistent
- FAISS CPU version: Good for moderate document sizes
- Full similarity search (k=10000): Simple but comprehensive retrieval
- Local LLM: Speed depends on hardware (CPU/GPU)

## 🧪 Testing

The project includes:
- **test.ipynb**: Jupyter notebook for interactive testing
- **Samples/**: 15 contract PDFs for testing the system
- Can be tested by running rag.py directly (has main block)

## 📊 Project Statistics

- **Total Lines of Code**: ~338 lines (server.py + rag.py + index.html)
- **Dependencies**: 23 Python packages
- **Sample Documents**: 15 contract PDFs
- **API Endpoints**: 6 endpoints
- **Core Functions**: 5 main functions in rag.py

## 🔮 Potential Enhancements

Based on the codebase structure, potential improvements could include:
1. Persistent vector store (save to disk)
2. Support for multiple file formats (DOCX, TXT)
3. Authentication system
4. Batch document processing
5. Advanced chunking strategies
6. Chat history export
7. Custom LLM parameters (temperature, top_k)
8. Document deletion/management
9. Search result highlighting
10. Multi-language support

## 🏁 Summary

HiLabs Chat Bot is a well-architected, production-ready RAG application that demonstrates:
- Clean separation of concerns (server, RAG logic, UI)
- Modern AI/ML best practices
- Privacy-first approach with local LLM
- Practical use case for document Q&A
- Scalable session-based architecture

The project successfully combines Flask web development, LangChain's RAG capabilities, and Llama 3.1's language understanding to create a powerful yet simple document analysis tool. Its focus on local processing makes it ideal for handling sensitive documents like contracts, legal papers, or confidential business materials.

## 📝 Notes

- The system currently supports one PDF per session (uses index 0 in pdf_paths)
- Vector store is not persisted between server restarts
- Ollama must be running for the application to work
- Requires sufficient RAM for FAISS index and LLM inference
- Processing time varies based on PDF size and hardware capabilities
