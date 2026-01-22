---
title: Image Text and Diagram Extractor
emoji: 📄
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
---

# Image Text & Diagram Extractor

Upload images containing text, notes, diagrams, or handwritten content. The app will:

1. **Extract text** using Tesseract OCR
2. **Generate a PDF** containing both the original images and extracted text

## Features

- Supports multiple image uploads
- Preserves original images in output PDF
- Extracts text from printed and handwritten content
- Download PDF or copy text directly

## Usage

1. Upload one or more images
2. Click "Extract & Generate PDF"
3. Download the generated PDF or copy the extracted text

## Tech Stack

- Gradio (UI)
- Tesseract OCR (Text extraction)
- FPDF (PDF generation)
- Pillow (Image processing)
