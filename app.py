from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from PIL import Image
import pytesseract
import io
import os

app = Flask(__name__)
CORS(app)

# HTML template for the upload interface
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>OCR App</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .upload-form {
            margin: 20px 0;
        }
        .result {
            margin-top: 20px;
            white-space: pre-wrap;
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 4px;
        }
        .error {
            color: red;
            margin-top: 10px;
        }
        .loading {
            display: none;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>OCR Text Extraction</h1>
        <p>Upload an image to extract text using Tesseract OCR.</p>
        
        <div class="upload-form">
            <form id="uploadForm">
                <input type="file" id="imageFile" accept="image/*" required>
                <button type="submit">Extract Text</button>
            </form>
            <div id="loading" class="loading">Processing...</div>
        </div>
        
        <div id="result" class="result"></div>
        <div id="error" class="error"></div>
    </div>

    <script>
        document.getElementById('uploadForm').onsubmit = async (e) => {
            e.preventDefault();
            const resultDiv = document.getElementById('result');
            const errorDiv = document.getElementById('error');
            const loadingDiv = document.getElementById('loading');
            const fileInput = document.getElementById('imageFile');
            
            resultDiv.textContent = '';
            errorDiv.textContent = '';
            
            if (!fileInput.files.length) {
                errorDiv.textContent = 'Please select an image file.';
                return;
            }

            const formData = new FormData();
            formData.append('image', fileInput.files[0]);
            
            loadingDiv.style.display = 'block';
            
            try {
                const response = await fetch('/ocr', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    resultDiv.textContent = data.text || 'No text was extracted from the image.';
                } else {
                    errorDiv.textContent = data.error || 'An error occurred during processing.';
                }
            } catch (error) {
                errorDiv.textContent = 'An error occurred while uploading the image.';
            } finally {
                loadingDiv.style.display = 'none';
            }
        };
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/ocr', methods=['POST'])
def ocr():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    file = request.files['image']
    
    if not file.filename:
        return jsonify({'error': 'No selected file'}), 400
        
    # Check file extension
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}
    if '.' not in file.filename or \
       file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        return jsonify({'error': 'Invalid file type. Please upload an image file.'}), 400

    try:
        # Read the image
        image = Image.open(file.stream)
        
        # Convert image to RGB if necessary
        if image.mode not in ('L', 'RGB'):
            image = image.convert('RGB')
            
        # Extract text
        text = pytesseract.image_to_string(image)
        
        if not text.strip():
            return jsonify({'text': 'No text was detected in the image.'})
            
        return jsonify({'text': text})
    except Exception as e:
        return jsonify({'error': f'Error processing image: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
