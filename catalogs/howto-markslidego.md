---
marp: true
title: Howto use MarkSlide Go
description: A quickstart tutorial with MarkSlide Go
author: Bernhard Wallisch (bernhard_wallisch@hotmail.com)
keywords: Markdown, MarkSlide, MarkSlide Go, MARP, MARPIT
url: https://codepunx.wordpress.com
theme: gaia
style: |
  .columns {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 1rem;
  }
paginate: true
footer: 'MarkSlide Go'
backgroundColor: #fff
backgroundImage: url('https://marp.app/assets/hero-background.svg')
---
<!--
_paginate: skip
_footer: ''
_class : lead
-->

![bg](marp/_template/images/background1.jpg)

# Howto use MarkSlide Go 

[https://github.com/BernLeWal/MarkSlideGo](https://github.com/BernLeWal/MarkSlideGo)

---
# MarkSlide Go

This project contains tools to manage a knowledge-base as hierarchicaly structured markdown-files. These files are converted to PDF- or HTML-slide decks using the MARP tool.

References:

* Markdown Presentation Ecosystem [MARP Official Site](https://marp.app)
* Markdown Explorer [VS Code Extension](https://github.com/BernLeWal/VSCode-MARX)
---
## Installation

* Create a [.env](.env) file in the project root. See [.env.sample](.env.sample)
* Install [Node.js](https://nodejs.org/en)  
* Install the Marp CLI client
* Install the [Marp for VS Code](https://marketplace.visualstudio.com/items?itemName=marp-team.marp-vscode) extension, and activate HTML
* Install Tesseract with better language files
* Install Python (>3.10), create virtual environment (venv) and activate it
* Install the necessary python libraries
---
## Usage

Use the following scripts to generate the slide-decks in various formats.
The scripts will iterate through the catalogs/ and create a slide-deck for every .md-file found there.

---
### Generate all slides

* Generate PDF (with outlines and notes): 
    ```shell
    python3 generate_all.py
    ```
* Generate PPTX : 
    ```shell
    python3 generate_all.py pptx
    ```
---
### Generate slides per course

In the courses/ directory a sub-dir for each (e.g. moodle) course is created.
Inside the sub-directories there are YAML-files, containing the course-structure filled with the slides-config per topic.

To generate all the slides for a moodle-course move inside the course-directory, and execute the following command:
```shell
~/dev/marp/courses/bic4_sam/$ python3 generate_course.py <coursefile>.yml
```
---
### Full-Text Search the Knowledge-Base

Simply use the search-function of VSCode which effectively will find the files and lines where the search expression fits (like the command line tool grep)

---
### Generate Text/MD out of PDF-Files (with OCR)

It is possible to fill the Knowledge-Base also with PDF-Files. To make them searchable, the contents of the PDFs need to be converted to a (Markdown-based) textfile.
Use the pdf2md.py tool to get Markdown text, pdf2text.py to get unformated text.
Change to the directory of the PDF-file and run the tool:

```shell
~/dev/marp/catalogs/$ python3 pdf2text.py SpringBoot3-Infografik.pdf
~/dev/marp/catalogs/$ python3 pdf2md.py SpringBoot3-Infografik.pdf
```
