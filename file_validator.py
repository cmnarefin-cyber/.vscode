import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)

# --- CONFIGURATION ---
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB limits

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return render_template('upload.html', error="No file part in the request.")
    
    file = request.files['file']
    
    if file.filename == '':
        return render_template('upload.html', error="No selected file.")
    
    if file:
        # 1. Validation: File Extension
        if not allowed_file(file.filename):
            return render_template('upload.html', 
                                   error=f"Extension not allowed. Supported: {', '.join(ALLOWED_EXTENSIONS)}")
        
        # 2. Validation: File Content Size (redundant with MAX_CONTENT_LENGTH but good practice)
        # Note: Werkzeug already handles stream limits, but we can catch it here if needed.
        
        # 3. Security: Sanitize filename
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        try:
            file.save(save_path)
            return render_template('upload.html', 
                                   success=f"File '{filename}' successfully validated and uploaded!")
        except Exception as e:
            return render_template('upload.html', error=f"Failed to save file: {str(e)}")

    return render_template('upload.html', error="Something went wrong.")

@app.errorhandler(413)
def request_entity_too_large(error):
    """Special handler for files exceeding MAX_CONTENT_LENGTH."""
    return render_template('upload.html', error="File too large! Max limit is 2MB."), 413

if __name__ == '__main__':
    print(f"[*] Validator running at http://localhost:5001")
    app.run(port=5001, debug=True)
