import os
import subprocess
import secrets
import requests
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, jsonify, send_from_directory, session, redirect, url_for
from dotenv import load_dotenv
from forensic_engine import ingestor, analyzer, integrator, reporter

try:
    import psutil
except ImportError:
    psutil = None


import logging

# Load environment variables from .env
load_dotenv()

# Suppress standard Flask/Werkzeug console spam
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI", "http://localhost:5002/callback")

# --- AUTH MIDDLEWARE ---
@app.before_request
def require_oauth():
    allowed_routes = ['login', 'callback', 'static', 'favicon']
    if request.endpoint not in allowed_routes and not session.get('access_token'):
        return redirect(url_for('login'))

@app.route('/login')
def login():
    if not CLIENT_ID or not CLIENT_SECRET:
        return "<h1 style='color:red'>ERROR: GITHUB_CLIENT_ID / SECRET missing from .env!</h1>", 500
    state = secrets.token_hex(16)
    session['oauth_state'] = state
    url = f"https://github.com/login/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&state={state}&scope=read:user"
    return f'''
    <div style="background:#020408;color:#00ff9d;height:100vh;display:flex;align-items:center;justify-content:center;font-family:monospace;flex-direction:column;">
        <h1 style="letter-spacing:3px;">RESTRICTED FORENSIC SUITE</h1>
        <p style="color:#8e9aaf;">Authentication required to view intelligence.</p>
        <a href="{url}" style="padding:15px 30px; border:1px solid #00ff9d; color:#00ff9d; text-decoration:none; margin-top:30px; text-transform:uppercase; font-weight:bold; transition:0.3s; background:rgba(0,255,157,0.1);">[ INITIATE GITHUB HANDSHAKE ]</a>
    </div>
    '''

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code: return "No code", 400
    expected_state = session.pop('oauth_state', None)
    if request.args.get('state') != expected_state: return "CSRF Error", 400
    
    resp = requests.post("https://github.com/login/oauth/access_token", data={
        "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "code": code, "redirect_uri": REDIRECT_URI
    }, headers={"Accept": "application/json"})
    
    token = resp.json().get("access_token")
    if not token: return "Failed to authenticate with GitHub", 400
    session['access_token'] = token
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def index():
    return render_template('forensic.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'forensic_intelligence_seal.png', mimetype='image/png')

@app.route('/ingest', methods=['POST'])
def ingest():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if not file or file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # SECURITY: Prevent Path Traversal
    safe_name = secure_filename(file.filename)
    if not safe_name:
        safe_name = f"unnamed_file_{secrets.token_hex(4)}"
        
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_name)
    file.save(file_path)
    
    try:
        metadata = ingestor.process_file(file_path)
        return jsonify(metadata)
    except Exception as e:
        log.error(f"Ingestion failure: {e}")
        return jsonify({"error": "Engine processing failed."}), 500

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
        if psutil:
            # High-fidelity cross-platform telemetry using psutil
            cpu = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory().percent
            return jsonify({
                "cpu": f"{cpu}%",
                "memory": f"{memory}%",
                "status": "SECURE" if cpu < 80 else "CRITICAL",
                "platform": "PSUTIL_CORE"
            })
        
        # Fallback to PowerShell for Windows systems without psutil
        cmd = "(Get-CimInstance Win32_OperatingSystem).TotalVisibleMemorySize; (Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory; (Get-WmiObject Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average"
        result = subprocess.check_output(["powershell", "-Command", cmd], text=True)
        lines = [line.strip() for line in result.split("\n") if line.strip()]
        
        if len(lines) >= 3:
            total_mem = int(lines[0])
            free_mem = int(lines[1])
            cpu = lines[2]
            mem_usage = round((1 - (free_mem / total_mem)) * 100, 1)
            
            return jsonify({
                "cpu": f"{cpu}%",
                "memory": f"{mem_usage}%",
                "status": "SECURE" if float(cpu) < 80 else "CRITICAL",
                "platform": "POWERSHELL_FALLBACK"
            })
        return jsonify({"cpu": "N/A", "memory": "N/A", "status": "WARMUP"}), 200
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
