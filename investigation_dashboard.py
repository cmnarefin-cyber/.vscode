import os
import json
from flask import Flask, render_template, request, jsonify, send_from_directory
from forensic_engine import ingestor, analyzer, integrator, reporter

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('forensic.html')

@app.route('/ingest', methods=['POST'])
def ingest():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    
    metadata = ingestor.process_file(file_path)
    return jsonify(metadata)

@app.route('/query', methods=['POST'])
def query_intel():
    data = request.get_json()
    query = data.get('query', '')
    results = integrator.query_global_databases(query)
    return jsonify(results)

@app.route('/generate_report', methods=['POST'])
def generate_report():
    data = request.get_json()
    # data would contain metadata and analysis results
    report_content = reporter.generate_report(data)
    return jsonify({"report": report_content})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    print("[*] Senior Government Intelligence Dashboard active at http://localhost:5002")
    app.run(port=5002, debug=True)
