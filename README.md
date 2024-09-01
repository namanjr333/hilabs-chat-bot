# HiLabs Chat Bot

Welcome to the HiLabs Chat Bot project! This bot utilizes the lightweight, open-source version of Llama 3.1 (Ollama) and runs locally to provide efficient and effective responses.

## Architecture

1. **PDF to Docs Conversion**: Converts PDF files to text documents.
2. **Document Embedding**: Embeds the text documents for easier retrieval.
3. **Vector DB Storage**: Stores the embedded documents in a vector database.
4. **Similarity Search**: Performs similarity searches to find relevant documents.
5. **LLM Interaction**: Sends the retrieved documents along with the user's question to the LLM for response.

## Requirements

- **Llama 3.1**: Ensure you have the Llama 3.1 model installed.
- **Installation Command**:
  ```bash
  curl -sSL https://ollama.com/install.sh | bash
  ```
- **Pull Llama 3.1**:
  ```bash
  ollama pull llama-3.1
  ```

## Setup

1. **Create a Virtual Environment**:
   ```bash
   python -m venv .venv
   ```
2. **Activate the Virtual Environment**:
   ```bash
   source .venv/bin/activate
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Start the Server**:
   ```bash
   python server.py
   ```
5. **Access the Application**: Open your web browser and navigate to [http://localhost:5000](http://localhost:5000).

## Usage

1. **Start a New Session**: Click on "New Session".
2. **Upload a PDF File**: Upload the file you wish to process.
3. **Process the File**: The application will process and convert the file.
4. **Ask a Question**: Enter your question in the provided field.
5. **Get the Answer**: Receive the answer based on the content of the uploaded PDF.
