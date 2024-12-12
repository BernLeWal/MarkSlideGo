# MarkSlide Go

This project contains tools to manage a knowledge-base as hierarchicaly structured markdown-files. These files are converted to PDF- or HTML-slide decks using the MARP tool.

References:

* Markdown Presentation Ecosystem [MARP Official Site](https://marp.app)
* Markdown Explorer [VS Code Extension](https://github.com/BernLeWal/VSCode-MARX)

TODO:
* package.json --> fix "themeSet" property to use catalog's _template

## Installation

* Create a [.env](.env) file in the project root. See [.env.sample](.env.sample)
* Install [Node.js](https://nodejs.org/en)  
    The Marp-Tool uses NodeJs > v16 which has to be installed prior to execution of the CLI tool.  
    Set the path to the npx-executable in the [.env](.env) file.
* Install the Marp CLI client
    For a local install use:
    ```shell
    npm install --save-dev @marp-team/marp-cli    
    ```
    Check if it works using:
    ```shell
    npx @marp-team/marp-cli@latest
    ```
* Install Google-Chrome (required for the html-rendering)
* Install the [Marp for VS Code](https://marketplace.visualstudio.com/items?itemName=marp-team.marp-vscode) extension
* Activate VS Code-Setting: Markdown > Marp: Enable HTML  
    to support html-based styling and multi-column slides, see [https://github.com/orgs/marp-team/discussions/192#discussioncomment-1517399]
* Install Tesseract  
    Installers see [https://www.baeldung.com/java-ocr-tesseract#setup], Set the path to the tesseract-executable in the [.env](.env) file.
* Download and install better language files from [https://github.com/tesseract-ocr/tessdata/tree/main] (just replace the previously installed .traineddata files)
* Install Python (>3.10), create virtual environment (venv) and activate it
* Install the necessary python libraries
    ```shell
    pip install -r requirements.txt
    ```

## Usage

Use the following scripts to generate the slide-decks in various formats.
The scripts will iterate through the catalogs/ and create a slide-deck for every .md-file found there.

### Generate all slides

* Generate PDF (with outlines and notes): ```python3 generate_all.py```
* Generate PPTX : ```python3 generate_all.py pptx```

### Generate slides per course

see [courses/README.md](./courses/README.md)

### Full-Text Search the Knowledge-Base

Simply use the search-function of VSCode which effectively will find the files and lines where the search expression fits (like the command line tool grep)

### Generate Text/MD out of PDF-Files (with OCR)

It is possible to fill the Knowledge-Base also with PDF-Files. To make them searchable, the contents of the PDFs need to be converted to a (Markdown-based) textfile.
Use the pdf2md.py tool to get Markdown text, pdf2text.py to get unformated text.
Change to the directory of the PDF-file and run the tool:

```shell
~/dev/marp/catalogs/$ python3 pdf2text.py SpringBoot3-Infografik.pdf
~/dev/marp/catalogs/$ python3 pdf2md.py SpringBoot3-Infografik.pdf
```
