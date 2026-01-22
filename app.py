from flask import Flask, render_template_string, request, send_file
import easyocr
from PIL import Image
from fpdf import FPDF
import tempfile
import os
import numpy as np

app = Flask(__name__)

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Image Text Extractor</title>
    <style>
        body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; background: #f5f5f5; }
        .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; }
        .upload-form { text-align: center; margin: 30px 0; }
        input[type="file"] { margin: 20px 0; }
        button { background: #007bff; color: white; padding: 12px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        button:hover { background: #0056b3; }
        .result { margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 5px; }
        .result h3 { margin-top: 0; }
        textarea { width: 100%; height: 200px; margin: 10px 0; padding: 10px; }
        .download-btn { background: #28a745; margin-top: 15px; }
        .download-btn:hover { background: #1e7e34; }
        .note { font-size: 12px; color: #666; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Image Text Extractor</h1>
        <p style="text-align: center;">Upload an image to extract text and generate PDF</p>
        <p class="note">Powered by EasyOCR - AI-based text recognition</p>

        <form class="upload-form" method="POST" enctype="multipart/form-data">
            <input type="file" name="image" accept="image/*" required><br>
            <button type="submit">Extract Text & Generate PDF</button>
        </form>

        {% if extracted_text %}
        <div class="result">
            <h3>Extracted Text:</h3>
            <textarea readonly>{{ extracted_text }}</textarea>
            <a href="/download"><button class="download-btn">Download PDF</button></a>
        </div>
        {% endif %}
    </div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    extracted_text = None

    if request.method == 'POST':
        if 'image' in request.files:
            file = request.files['image']
            if file.filename:
                # Open image
                img = Image.open(file)
                img_array = np.array(img)

                # Extract text using EasyOCR
                results = reader.readtext(img_array)
                extracted_text = '\n'.join([text[1] for text in results])

                if not extracted_text.strip():
                    extracted_text = "No text detected"

                # Create PDF
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", "B", 16)
                pdf.cell(0, 10, "Extracted Document", ln=True, align="C")
                pdf.ln(10)

                # Save temp image
                temp_img = os.path.join(tempfile.gettempdir(), "temp.jpg")
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                img.save(temp_img, "JPEG")

                pdf.image(temp_img, x=10, w=190)
                pdf.ln(85)

                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 10, "Extracted Text:", ln=True)
                pdf.set_font("Arial", "", 10)
                clean_text = extracted_text.encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(0, 5, clean_text)

                # Save PDF
                pdf_path = os.path.join(tempfile.gettempdir(), "output.pdf")
                pdf.output(pdf_path)
                os.remove(temp_img)

    return render_template_string(HTML, extracted_text=extracted_text)

@app.route('/download')
def download():
    pdf_path = os.path.join(tempfile.gettempdir(), "output.pdf")
    return send_file(pdf_path, as_attachment=True, download_name="extracted_document.pdf")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)
