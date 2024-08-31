import os
from flask import Flask, session, request, jsonify
from werkzeug.utils import secure_filename
from rag import create_vector_store, add_documents_to_vector_store, get_documents, get_answer

app = Flask(__name__)
app.secret_key = 'super_secret_key'

UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    
db = {}

@app.route('/get-session-key', methods=['GET'])
def get_session_key():
    import uuid
    session_key = str(uuid.uuid4())
    session['key'] = session_key
    db[session_key] = {
        'vector_store': create_vector_store(),
        'pdf_paths': []
    }
    return jsonify({'message': 'Session key set successfully'}), 200

@app.route('/upload-pdf', methods=['POST'])
def upload_pdf():
    if 'pdf' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['pdf']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and file.filename.endswith('.pdf'):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        db[session['key']]['pdf_paths'].append(file_path)
        return jsonify({'message': 'File uploaded successfully', 'filename': filename}), 200
    
    return jsonify({'error': 'Invalid file format. Please upload a PDF.'}), 400

@app.route('/process-pdf', methods=['GET'])
def process_pdf():
    vector_store = db[session['key']]['vector_store']
    file_path = db[session['key']]['pdf_paths'][0]
    docs = get_documents(file_path)
    add_documents_to_vector_store(vector_store, docs[:20])
    return jsonify({'message': 'PDF processed successfully'}), 200
    

@app.route('/ask-question', methods=['POST'])
def ask_question():
    vector_store = db[session['key']]['vector_store']
    question = request.json['question']
    response = get_answer(vector_store, question)
    return jsonify({'response': response}), 200


if __name__ == '__main__':
    app.run(debug=True)
