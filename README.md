# HiLabs AI Document Assistant (Optimized)

Welcome to the **optimized** HiLabs AI Document Assistant! This enhanced version features a modern, responsive web interface, improved RAG performance, and better error handling.

## ✨ New Features

### 🎨 Modern Interface
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Drag & Drop**: Simply drag PDF files to upload
- **Real-time Progress**: Visual progress bars and loading indicators
- **Chat Interface**: Modern chat bubbles with smooth animations
- **Status Notifications**: Clear success/error messages

### ⚡ Performance Improvements
- **Optimized Chunking**: Increased chunk size from 100 to 1000 characters for better context
- **Smart Retrieval**: Reduced similarity search from 10,000 to 5 relevant chunks
- **Better Prompts**: Enhanced prompts for more accurate responses
- **Logging**: Comprehensive logging for debugging and monitoring

### 🛡️ Security & Reliability
- **Input Validation**: File type, size, and content validation
- **Session Management**: Secure session handling with automatic cleanup
- **Error Handling**: Graceful error handling throughout the application
- **Health Checks**: Built-in health monitoring endpoints

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Ollama installed and running
- llama3.1 model downloaded

### Installation

1. **Install Ollama** (if not already installed):
   ```bash
   curl -sSL https://ollama.com/install.sh | bash
   ```

2. **Start Ollama and pull the model**:
   ```bash
   ollama serve &
   ollama pull llama3.1
   ```

3. **Set up the Python environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Start the server**:
   ```bash
   python server.py
   ```

5. **Open your browser** and navigate to:
   ```
   http://localhost:8000
   ```

## 📖 How to Use

1. **Start a New Session**: Click "New Session" to initialize your workspace
2. **Upload a PDF**: Drag and drop a PDF file or click to browse
3. **Process the Document**: Click "Process Document" to analyze the content
4. **Ask Questions**: Type your questions in the chat interface

## 🏗️ Architecture

The application consists of three main components:

### 1. **RAG Engine** (`rag.py`)
- **Document Processing**: Extracts and chunks PDF content
- **Vector Storage**: Uses FAISS for efficient similarity search
- **LLM Integration**: Connects to Ollama's llama3.1 model
- **Smart Retrieval**: Optimized context retrieval and response generation

### 2. **Web Server** (`server.py`)
- **Flask Backend**: RESTful API with session management
- **File Handling**: Secure file upload and validation
- **Error Management**: Comprehensive error handling and logging
- **Health Monitoring**: Built-in health check endpoints

### 3. **Frontend** (`templates/index.html`)
- **Modern UI**: Responsive design with gradient backgrounds
- **Interactive Elements**: Drag-and-drop, progress bars, animations
- **Real-time Chat**: Dynamic message handling with typing indicators
- **Mobile Friendly**: Optimized for all screen sizes

## 🔧 Configuration

### Environment Variables
- `SECRET_KEY`: Flask secret key (default: auto-generated)
- `UPLOAD_FOLDER`: File upload directory (default: `uploads/`)
- `MAX_CONTENT_LENGTH`: Maximum file size in bytes (default: 16MB)

### RAG Settings
- **Chunk Size**: 1000 characters (optimized for context retention)
- **Chunk Overlap**: 100 characters (ensures continuity)
- **Similarity Search**: Top 5 most relevant chunks
- **Model**: llama3.1 via Ollama

## 🛠️ API Endpoints

- `GET /` - Main application interface
- `GET /get-session-key` - Create new session
- `POST /upload-pdf` - Upload PDF file
- `GET /process-pdf` - Process uploaded document
- `POST /ask-question` - Submit questions
- `GET /get-messages` - Retrieve chat history
- `GET /health` - Health check endpoint
- `GET /session-info` - Session information

## 📊 Sample Files

The `Samples/` directory contains 15 contract PDF files for testing:
- Contract 1.pdf through Contract 15.pdf
- Various sizes from 117KB to 3.3MB
- Perfect for testing document analysis capabilities

## 🔍 Testing

Test the RAG system directly:
```bash
python rag.py
```

Check server health:
```bash
curl http://localhost:8000/health
```

## 🚨 Troubleshooting

### Common Issues

1. **"Ollama not found"**
   - Ensure Ollama is installed and running
   - Check if llama3.1 model is downloaded: `ollama list`

2. **"Port already in use"**
   - The server runs on port 8000 by default
   - Kill existing processes: `pkill -f server.py`

3. **"File upload fails"**
   - Check file size (max 16MB)
   - Ensure file is a valid PDF
   - Verify upload directory permissions

4. **"PDF processing errors"**
   - Ensure pdfplumber is installed: `pip install pdfplumber`
   - Check if PDF is readable/not password protected

## 💡 Performance Tips

1. **For Large Documents**: The system works best with documents under 10MB
2. **Optimal Questions**: Ask specific questions about document content
3. **Session Management**: Start new sessions for different documents
4. **Memory Usage**: Monitor system resources with multiple concurrent users

## 🔄 Updates from Original

### Interface Improvements
- ✅ Modern gradient design with glassmorphism effects
- ✅ Drag-and-drop file upload
- ✅ Real-time progress indicators
- ✅ Responsive mobile-friendly layout
- ✅ Chat-style conversation interface

### Backend Enhancements
- ✅ Optimized RAG configuration (1000 char chunks vs 100)
- ✅ Smart similarity search (5 results vs 10,000)
- ✅ Comprehensive error handling and logging
- ✅ Session management with automatic cleanup
- ✅ File validation and security improvements

### Developer Experience
- ✅ Health check endpoints for monitoring
- ✅ Detailed logging for debugging
- ✅ Type hints and documentation
- ✅ Modular code structure

## 📝 License

This project is part of the HiLabs ecosystem. Please refer to your organization's licensing terms.

---

**Enjoy your enhanced document analysis experience! 🚀**
