import os
import subprocess
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

@app.route('/telemetry')
def get_telemetry():
    try:
        # Quick PowerShell check for CPU and Free RAM
        cmd = "Get-CimInstance Win32_OperatingSystem | Select-Object -Property TotalVisibleMemorySize, FreePhysicalMemory; (Get-WmiObject Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average"
        result = subprocess.check_output(["powershell", "-Command", cmd], text=True)
        lines = [line.strip() for line in result.split("\n") if line.strip()]
        
        # Parse output (simplified)
        cpu = lines[-1]
        mem_info = lines[1].split()
        total_mem = int(mem_info[0])
        free_mem = int(mem_info[1])
        mem_usage = round((1 - (free_mem / total_mem)) * 100, 1)
        
        return jsonify({
            "cpu": f"{cpu}%",
            "memory": f"{mem_usage}%",
            "status": "SECURE" if float(cpu) < 80 else "CRITICAL"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    print("[*] Senior Government Intelligence Dashboard active at http://localhost:5002")
    app.run(port=5002, debug=True)
