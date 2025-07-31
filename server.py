import os
import uuid
import logging
from datetime import datetime, timedelta
from flask import Flask, session, request, jsonify, render_template
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from rag import create_vector_store, add_documents_to_vector_store, get_documents, get_answer, test_system

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')
    UPLOAD_FOLDER = 'uploads/'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'pdf'}
    SESSION_TIMEOUT_MINUTES = 60

config = Config()
app.config.from_object(config)

# Ensure upload directory exists
if not os.path.exists(config.UPLOAD_FOLDER):
    os.makedirs(config.UPLOAD_FOLDER)
    logger.info(f"Created upload directory: {config.UPLOAD_FOLDER}")

# In-memory database for sessions
db = {}
session_timestamps = {}

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS

def cleanup_expired_sessions():
    """Remove expired sessions from memory."""
    current_time = datetime.now()
    expired_sessions = []
    
    for session_id, timestamp in session_timestamps.items():
        if current_time - timestamp > timedelta(minutes=config.SESSION_TIMEOUT_MINUTES):
            expired_sessions.append(session_id)
    
    for session_id in expired_sessions:
        if session_id in db:
            # Clean up uploaded files
            try:
                session_data = db[session_id]
                for file_path in session_data.get('pdf_paths', []):
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        logger.info(f"Cleaned up file: {file_path}")
            except Exception as e:
                logger.error(f"Error cleaning up files for session {session_id}: {e}")
            
            del db[session_id]
            del session_timestamps[session_id]
            logger.info(f"Cleaned up expired session: {session_id}")

def validate_session():
    """Validate current session."""
    if 'key' not in session:
        return False, "No active session"
    
    session_key = session['key']
    if session_key not in db:
        return False, "Session not found"
    
    # Update session timestamp
    session_timestamps[session_key] = datetime.now()
    return True, "Valid session"

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Internal server error: {e}")
    return jsonify({'error': 'Internal server error occurred.'}), 500

@app.route('/')
def home():
    """Serve the main page."""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error serving home page: {e}")
        return jsonify({'error': 'Error loading page'}), 500

@app.route('/get-session-key', methods=['GET'])
def get_session_key():
    """Create a new session."""
    try:
        # Clean up expired sessions periodically
        cleanup_expired_sessions()
        
        session_key = str(uuid.uuid4())
        session['key'] = session_key
        
        # Test system before creating session
        if not test_system():
            logger.error("System test failed during session creation")
            return jsonify({'error': 'System not ready. Please ensure Ollama is running.'}), 503
        
        db[session_key] = {
            'vector_store': create_vector_store(),
            'pdf_paths': [],
            'messages': [],
            'created_at': datetime.now()
        }
        session_timestamps[session_key] = datetime.now()
        
        logger.info(f"Created new session: {session_key}")
        return jsonify({'message': 'Session created successfully', 'session_id': session_key}), 200
        
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        return jsonify({'error': 'Failed to create session'}), 500

@app.route('/upload-pdf', methods=['POST'])
def upload_pdf():
    """Handle PDF file upload."""
    try:
        # Validate session
        is_valid, message = validate_session()
        if not is_valid:
            return jsonify({'error': message}), 401
        
        # Check if file is in request
        if 'pdf' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['pdf']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only PDF files are allowed.'}), 400
        
        # Secure filename and create session directory
        filename = secure_filename(file.filename)
        session_key = session['key']
        session_dir = os.path.join(config.UPLOAD_FOLDER, session_key)
        
        if not os.path.exists(session_dir):
            os.makedirs(session_dir)
        
        file_path = os.path.join(session_dir, filename)
        
        # Check file size before saving
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > config.MAX_CONTENT_LENGTH:
            return jsonify({'error': f'File too large. Maximum size is {config.MAX_CONTENT_LENGTH // (1024*1024)}MB.'}), 413
        
        # Save file
        file.save(file_path)
        db[session_key]['pdf_paths'].append(file_path)
        
        logger.info(f"File uploaded successfully: {filename} ({file_size} bytes) for session {session_key}")
        return jsonify({
            'message': 'File uploaded successfully', 
            'filename': filename,
            'size': file_size
        }), 200
        
    except RequestEntityTooLarge:
        return jsonify({'error': 'File too large'}), 413
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        return jsonify({'error': 'Failed to upload file'}), 500

@app.route('/process-pdf', methods=['GET'])
def process_pdf():
    """Process the uploaded PDF file."""
    try:
        # Validate session
        is_valid, message = validate_session()
        if not is_valid:
            return jsonify({'error': message}), 401
        
        session_key = session['key']
        session_data = db[session_key]
        
        # Check if PDF is uploaded
        if not session_data['pdf_paths']:
            return jsonify({'error': 'No PDF file uploaded'}), 400
        
        file_path = session_data['pdf_paths'][0]  # Use first uploaded file
        
        # Check if file exists
        if not os.path.exists(file_path):
            return jsonify({'error': 'Uploaded file not found'}), 404
        
        # Process document
        logger.info(f"Processing PDF: {file_path}")
        docs = get_documents(file_path)
        
        if not docs:
            return jsonify({'error': 'No content could be extracted from the PDF'}), 400
        
        # Add to vector store
        vector_store = session_data['vector_store']
        add_documents_to_vector_store(vector_store, docs)
        
        logger.info(f"PDF processed successfully: {len(docs)} chunks for session {session_key}")
        return jsonify({
            'message': 'PDF processed successfully',
            'chunks': len(docs)
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        return jsonify({'error': 'Failed to process PDF. Please ensure the file is a valid PDF.'}), 500

@app.route('/ask-question', methods=['POST'])
def ask_question():
    """Handle question answering."""
    try:
        # Validate session
        is_valid, message = validate_session()
        if not is_valid:
            return jsonify({'error': message}), 401
        
        # Validate request data
        if not request.json or 'question' not in request.json:
            return jsonify({'error': 'No question provided'}), 400
        
        question = request.json['question'].strip()
        if not question:
            return jsonify({'error': 'Empty question provided'}), 400
        
        if len(question) > 1000:  # Reasonable question length limit
            return jsonify({'error': 'Question too long. Please keep it under 1000 characters.'}), 400
        
        session_key = session['key']
        session_data = db[session_key]
        
        # Check if document is processed
        if not session_data['pdf_paths']:
            return jsonify({'error': 'No document uploaded'}), 400
        
        vector_store = session_data['vector_store']
        
        # Get answer
        logger.info(f"Processing question for session {session_key}: {question[:50]}...")
        response = get_answer(vector_store, question)
        
        # Store conversation
        conversation = {
            'question': question,
            'response': response,
            'timestamp': datetime.now().isoformat()
        }
        session_data['messages'].append(conversation)
        
        logger.info(f"Question answered successfully for session {session_key}")
        return jsonify({'response': response}), 200
        
    except Exception as e:
        logger.error(f"Error answering question: {e}")
        return jsonify({'error': 'Failed to process question. Please try again.'}), 500

@app.route('/get-messages', methods=['GET'])
def get_messages():
    """Get conversation history."""
    try:
        # Validate session
        is_valid, message = validate_session()
        if not is_valid:
            return jsonify({'error': message}), 401
        
        session_key = session['key']
        messages = db[session_key]['messages']
        
        return jsonify({'messages': messages}), 200
        
    except Exception as e:
        logger.error(f"Error retrieving messages: {e}")
        return jsonify({'error': 'Failed to retrieve messages'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        system_status = test_system()
        return jsonify({
            'status': 'healthy' if system_status else 'unhealthy',
            'ollama_available': system_status,
            'timestamp': datetime.now().isoformat()
        }), 200 if system_status else 503
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/session-info', methods=['GET'])
def session_info():
    """Get current session information."""
    try:
        # Validate session
        is_valid, message = validate_session()
        if not is_valid:
            return jsonify({'error': message}), 401
        
        session_key = session['key']
        session_data = db[session_key]
        
        info = {
            'session_id': session_key,
            'created_at': session_data['created_at'].isoformat(),
            'files_uploaded': len(session_data['pdf_paths']),
            'messages_count': len(session_data['messages']),
            'last_activity': session_timestamps[session_key].isoformat()
        }
        
        return jsonify(info), 200
        
    except Exception as e:
        logger.error(f"Error getting session info: {e}")
        return jsonify({'error': 'Failed to get session info'}), 500

if __name__ == '__main__':
    logger.info("Starting HiLabs AI Document Assistant Server")
    logger.info(f"Upload folder: {config.UPLOAD_FOLDER}")
    logger.info(f"Max file size: {config.MAX_CONTENT_LENGTH // (1024*1024)}MB")
    
    # Test system on startup
    if not test_system():
        logger.error("System test failed on startup. Please ensure Ollama is running with llama3.1 model.")
        print("\nERROR: Ollama system test failed!")
        print("Please ensure:")
        print("1. Ollama is installed and running")
        print("2. llama3.1 model is available (run: ollama pull llama3.1)")
        exit(1)
    
    logger.info("System test passed. Starting server...")
    app.run(debug=True, host='0.0.0.0', port=8000)
