import gradio as gr
import pytesseract
from PIL import Image
from fpdf import FPDF
import os
import tempfile

# For Hugging Face Spaces - Tesseract is pre-installed
# Locally on Windows, you may need to set the path:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_and_create_pdf(images):
    """
    Takes uploaded images, extracts text using OCR,
    and creates a PDF with both text and original images.
    """
    if images is None or len(images) == 0:
        return None, "Please upload at least one image."

    # Create PDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    all_extracted_text = []

    for idx, img_path in enumerate(images):
        # Open image
        img = Image.open(img_path)

        # Extract text using OCR
        extracted_text = pytesseract.image_to_string(img)
        all_extracted_text.append(f"--- Page {idx + 1} ---\n{extracted_text}")

        # Add page to PDF
        pdf.add_page()

        # Add title
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, f"Page {idx + 1}", ln=True, align="C")
        pdf.ln(5)

        # Add original image to PDF
        # Save temp image for PDF embedding
        temp_img_path = os.path.join(tempfile.gettempdir(), f"temp_img_{idx}.jpg")

        # Convert to RGB if necessary (for PNG with transparency)
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        img.save(temp_img_path, "JPEG", quality=85)

        # Calculate image dimensions to fit page
        page_width = 190  # PDF page width minus margins
        img_width, img_height = img.size
        aspect_ratio = img_height / img_width
        display_width = min(page_width, 170)
        display_height = display_width * aspect_ratio

        # Limit height
        if display_height > 150:
            display_height = 150
            display_width = display_height / aspect_ratio

        # Add image centered
        x_pos = (210 - display_width) / 2
        pdf.image(temp_img_path, x=x_pos, y=pdf.get_y(), w=display_width)
        pdf.ln(display_height + 10)

        # Add extracted text section
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Extracted Text:", ln=True)
        pdf.set_font("Arial", "", 10)

        # Handle text encoding and add to PDF
        clean_text = extracted_text.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 5, clean_text if clean_text.strip() else "No text detected")

        # Clean up temp file
        if os.path.exists(temp_img_path):
            os.remove(temp_img_path)

    # Save PDF to temp file
    output_pdf_path = os.path.join(tempfile.gettempdir(), "extracted_output.pdf")
    pdf.output(output_pdf_path)

    # Combine all extracted text
    full_text = "\n\n".join(all_extracted_text)

    return output_pdf_path, full_text

# Create Gradio Interface
with gr.Blocks(title="Image Text & Diagram Extractor") as app:
    gr.Markdown("""
    # Image Text & Diagram Extractor
    Upload images (notes, documents, diagrams) and get:
    - **Extracted text** using OCR
    - **PDF** with original images + extracted text
    """)

    with gr.Row():
        with gr.Column():
            image_input = gr.File(
                label="Upload Images",
                file_count="multiple",
                file_types=["image"],
                type="filepath"
            )
            submit_btn = gr.Button("Extract & Generate PDF", variant="primary")

        with gr.Column():
            pdf_output = gr.File(label="Download PDF")
            text_output = gr.Textbox(
                label="Extracted Text",
                lines=15,
                show_copy_button=True
            )

    submit_btn.click(
        fn=extract_text_and_create_pdf,
        inputs=[image_input],
        outputs=[pdf_output, text_output]
    )

    gr.Markdown("""
    ---
    **How it works:**
    1. Upload one or more images
    2. Click 'Extract & Generate PDF'
    3. Download the PDF or copy the extracted text

    *Powered by Tesseract OCR*
    """)

# Launch the app
if __name__ == "__main__":
    app.launch()
