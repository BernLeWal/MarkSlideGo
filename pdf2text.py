#!/bin/python
"""Module to convert a PDF file to a Text file using OCR."""
import os
import sys
import tempfile
import pytesseract
from PIL import Image
import fitz  # this is pymupdf
from tqdm.autonotebook import tqdm
from dotenv import load_dotenv


load_dotenv()  # take environment variables from .env.
# Set the path to the installed tesseract OCR
pytesseract.pytesseract.Py = os.environ.get('TESSERACT_CMD', '')
if not os.path.exists(pytesseract.pytesseract.Py):
    print(f"Error: Tesseract not found at {pytesseract.pytesseract.Py}")
    print("Please install Tesseract OCR and set the TESSERACT_CMD environment variable "
    "to the .env file (or to the path of the installed tesseract executable).")
    sys.exit(1)

def pdf_to_text(file_path :str, text_path :str) ->None:
    """Convert a PDF file to a Text file using OCR."""
    print(f"Converting PDF {file_path} to Text {text_path} ...")
    temp_dir = tempfile.gettempdir()  # Returns the location of the temporary directory
    doc = fitz.open(file_path)
    for i in tqdm(range(len(doc)), unit="page", desc="Extracting pages"):
        for img in doc.get_page_images(i):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)
            if pix.n < 5:       # this is GRAY or RGB
                pix._writeIMG(f"{temp_dir}/p{i}.png", "png", 94)
            else:               # CMYK: convert to RGB first
                pix1 = fitz.Pixmap(fitz.csRGB, pix)
                pix1._writeIMG(f"{temp_dir}/p{i}.png", "png", 94)
                pix1 = None
            pix = None

    for i in tqdm(range(len(doc)), unit="page", desc="Extracting text"):
        image_path = f"{temp_dir}/p{i}.png"
        text = doc.load_page(i).get_text()
        if os.path.exists(image_path):
            # Recognize the text as string in image using pytesserct
            text += pytesseract.image_to_string(Image.open(image_path))

        # Save the text in a Text file
        with open(text_path, "w" if i == 0 else "a", encoding="utf-8") as f:
            f.write(text)
            f.write(f"\n\n<!-- Page {i+1} -->\n\n")
        if os.path.exists(image_path):
            os.remove(image_path)  # remove image after text extraction

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python {sys.argv[0]} <pdf_file_path> [<text_file_path>]")
        sys.exit(1)

    source = sys.argv[1]
    if len(sys.argv) > 2:
        target = sys.argv[2]
    else:
        target = source.replace(".pdf", ".txt")
    pdf_to_text(source, target)
