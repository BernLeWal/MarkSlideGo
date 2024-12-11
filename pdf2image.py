#!/bin/python
""" pdf2image.py """
import sys
import os
import fitz  # PyMuPDF

def pdf2image(pdf_filename :str, output_filename :str) ->None:
    """ Convert the first page of a PDF file to an image """
    try:
        # Open the PDF file
        pdf = fitz.open(pdf_filename)

        # Get the first page
        page = pdf[0]

        # Get the page as a pixmap (an image)
        pixmap = page.get_pixmap()

        # Save the image to the output path
        pixmap.save(output_filename)

        print(f"Successfully saved the first page of {pdf_filename} as {output_filename}")
    except Exception as e:
        print(f"An error occurred: {e}")



# Use the script from the command line: python script.py input.pdf output.png
if __name__ == "__main__":
    if len(sys.argv)<2:
        print(f"Usage: python {sys.argv[0]} <pdf_file|directory> [<output_file>]")
        sys.exit(1)

    if os.path.isdir(sys.argv[1]):
        for file in os.listdir(sys.argv[1]):
            if file.endswith(".pdf"):
                filename = file[:-4]
                print( f"Processing file {filename}" )
                pdf_path = filename + ".pdf"
                output_path = filename + ".jpg"
                pdf2image(pdf_path, output_path)
    else:
        pdf_path = sys.argv[1]
        if len(sys.argv)>2:
            output_path = sys.argv[2]
        else:
            output_path = pdf_path[:-4] + ".jpg"
        pdf2image(pdf_path, output_path)
