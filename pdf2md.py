#!/bin/python
""" convert the document to markdown """
import sys
import pathlib
import pymupdf4llm


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python {sys.argv[0]} <pdf_file_path> [<md_file_path>]")
        sys.exit(1)

    source = sys.argv[1]
    if len(sys.argv) > 2:
        target = sys.argv[2]
    else:
        target = source.replace(".pdf", ".md")

    md_text = pymupdf4llm.to_markdown(source)
    pathlib.Path(target).write_bytes(md_text.encode())
