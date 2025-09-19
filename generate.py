#!/usr/bin/env python3
""" Generate slides (as PDF, PPTX or HTML files) from Markdown files using Marp. """
import re
import os
import sys
import subprocess
import logging
import shutil
import zipfile
import yaml
from dotenv import load_dotenv


load_dotenv()  # take environment variables from .env.

# Setup logging
LOGGING_LEVEL = os.environ.get('LOGGING_LEVEL', 'INFO')  # default to INFO if no env var set
numeric_level = getattr(logging, LOGGING_LEVEL.upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError(f'Invalid log level: {LOGGING_LEVEL}')
logging.basicConfig(level=numeric_level)
logger = logging.getLogger(__name__)

# Set the path to the installed NodeJS
NPX_CMD = os.environ.get('NPX_CMD', '')
if not os.path.exists(NPX_CMD):
    logger.error("Error: npx not found at %s."
    "Please install NodeJS and set the NPX_CMD environment variable "
    "to the .env file (or to the path of the installed tesseract executable).", NPX_CMD)
    sys.exit(1)


TEMPLATE_DIR = os.environ.get('TEMPLATE_DIR', '')
def find_template_directory() -> None:
    # Find the template directory
    global TEMPLATE_DIR

    if TEMPLATE_DIR and os.path.exists(TEMPLATE_DIR):
        return
    
    current_dir = os.getcwd()
    while True:
        if "_template" in os.listdir(current_dir):
            TEMPLATE_DIR = os.path.abspath(os.path.join(current_dir, "_template"))
            break
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:
            TEMPLATE_DIR = None
            break
        current_dir = parent_dir


MARKSLIDE_DIR = os.environ.get('MARKSLIDE_DIR', '')
if not os.path.exists(MARKSLIDE_DIR):
    logger.error("Error: MARKSLIDE_DIR not found at %s."
    "Please set the MARKSLIDE_DIR environment variable "
    "to the .env file (or to the path of the installed MarkSlideGo scripts).", MARKSLIDE_DIR)
    sys.exit(1)



def correct_relative_paths(content : str, source_file : str, target_file : str) -> str:
    """ Correct relative paths in image/link-tags. """
    source_dir = os.path.dirname(source_file)
    target_dir = os.path.dirname(target_file)

    # Find image/link tags with relative paths
    # Ignore paths that start with "http://" or "https://"
    img_tags = re.findall(r'\[.*?\]\((?!http://|https://)(.*?)\)', content)

    for img_tag in img_tags:
        # Calculate the absolute path of the image relative to the source folder
        absolute_path = os.path.abspath(os.path.join(source_dir, img_tag))

        # Calculate the new relative path from the target folder to the file
        relative_path = os.path.relpath(absolute_path, target_dir).replace('\\', '/')

        # Replace the old relative-path with the new relative-path in the content
        content = content.replace(f'({img_tag})', f'({relative_path})')

    return content



def copy_assets_to_output(content: str, source_file: str, target_file: str) -> None:
    """ Copy the assets (images, etc.) to the output folder and correct the relative paths. """
    source_dir = os.path.dirname(source_file)
    target_dir = os.path.dirname(target_file)
    target_filename, _ = os.path.splitext(os.path.basename(target_file))
    target_assets_dir = os.path.join(target_dir, target_filename)
    if not os.path.exists(target_assets_dir):
        os.makedirs(target_assets_dir)

    # Find image/link tags with relative paths
    # Ignore paths that start with "http://" or "https://"
    img_tags = re.findall(r'\[.*?\]\((?!http://|https://)(.*?)\)', content)

    for img_tag in img_tags:
        # Calculate the absolute path of the image relative to the source folder
        asset_source_path = os.path.abspath(os.path.join(source_dir, img_tag))
        target_img_tag = os.path.basename(img_tag)
        asset_target_path = os.path.abspath(os.path.join(target_assets_dir, target_img_tag))
        try:
            shutil.copy2(asset_source_path, asset_target_path)
        except FileNotFoundError:
            logger.warning("Asset file %s not found (or is not readable) "
            "and can't be copied to %s!", asset_source_path, asset_target_path)
            continue

        # Calculate the new relative path from the target folder to the file
        relative_path = os.path.relpath(asset_target_path, target_dir).replace('\\', '/')

        # Replace the old relative-path with the new relative-path in the content
        content = content.replace(f'({img_tag})', f'({relative_path})')

    return content



def preprocess(source_file: str, target_file: str, placeholders: dict) -> None:
    """ Preprocess a Markdown file, to replace variables. """
    # Check if the source file exists and is readable
    if os.access(source_file, os.R_OK):
        logger.debug("Processing file: %s", source_file)
        logger.debug("Generating file: %s ...", target_file)

        # Prepare the template
        if not TEMPLATE_DIR:
            logger.error("Error: No templates found at %s. "
            "Please put your template files into the '/_template' subdirectory", os.getcwd() )
            sys.exit(1)
        template_file = os.path.join(TEMPLATE_DIR, 'template.md')
        logger.info("Using template from %s", template_file)
        logger.info("Working directory is %s", os.getcwd())
        with open(template_file, 'r', encoding="utf-8") as file:
            template = file.read()
        template = copy_assets_to_output(template, template_file, target_file)

        # Read the source content
        with open(source_file, 'r', encoding="utf-8") as file:
            content = file.read()
        content = copy_assets_to_output(content, source_file, target_file)

        # Put together template and content
        # take the first slide from the template (skipt that slide in the content)
        # and the rest from the content
        slides = content.split('\n---\n')
        remaining_slides = slides[2:]
        content = template + "\n---\n".join(remaining_slides)

        # Replace the placeholders in the content
        for key, value in placeholders.items():
            content = content.replace('{{' + key + '}}', value)

        with open(target_file, 'w', encoding="utf-8") as file:
            file.write(content)
    else:
        logger.warning("Source file %s not found or is not readable", source_file)



def preprocess_multiple(source_files: list, target_file: str, placeholders: dict) -> None:
    """ Preprocess multiple Markdown files, to replace variables. """

    # Prepare the template
    if not TEMPLATE_DIR:
        logger.error("Error: No templates found at %s. "
        "Please set put your template files into the '/_template' subdirectory", os.getcwd() )
        sys.exit(1)
    template_file = os.path.join(TEMPLATE_DIR, 'template.md')
    logger.info("Using template from %s", template_file)
    logger.info("Working directory is %s", os.getcwd())
    with open(template_file, 'r', encoding="utf-8") as file:
        template = file.read()
    template = copy_assets_to_output(template, template_file, target_file)
    toc = """

# Table of Contents

"""
    content = ""

    for source_file in source_files:
        # Check if the source_file exists and is readable
        if os.access(source_file, os.R_OK):
            logger.debug("Processing file: %s", source_file)

            # Read the source content
            with open(source_file, 'r', encoding="utf-8") as file:
                source_content = file.read()
                source_props = re.search('---\n(.*?)\n---', source_content, re.DOTALL).group(1)
                properties = yaml.safe_load(source_props)
                if 'title' in properties:
                    toc += f"* {properties['title']}\n"
                    content += f"""
<!--
_class: lead
_paginate: skip
_footer: ''
-->

# {properties['title']}

---
"""
            source_content = copy_assets_to_output(source_content, source_file, target_file)

            # Put together template and content
            # take the first slide from the template (skipt that slide in the content)
            # and the rest from the content
            slides = source_content.split('\n---\n')
            remaining_slides = slides[2:]
            content = content + "\n---\n".join(remaining_slides)
        else:
            logger.warning("Source file %s not found or is not readable", source_file)

    # Build the complete content
    toc += "\n---\n"
    content = template + toc + content

    # Replace the placeholders in the content
    for key, value in placeholders.items():
        content = content.replace('{{' + key + '}}', value)

    logger.debug("Generating file: %s ...", target_file)
    with open(target_file, 'w', encoding="utf-8") as file:
        file.write(content)



def is_source_newer(sourcefile :str, targetfile :str) -> bool:
    """ Check if the source file is newer than the target file. """
    if not os.path.exists(sourcefile):
        return False
    if not os.path.exists(targetfile):
        return True

    # Get the last modification times for both files
    sourcefile_time = os.path.getmtime(sourcefile)
    targetfile_time = os.path.getmtime(targetfile)

    # Compare the modification times
    return bool(sourcefile_time > targetfile_time)



def is_any_source_newer(sourcefiles :list, targetfile :str) -> bool:
    """ Check is any of the source files is newer than the target file. """
    if not os.path.exists(targetfile):
        return True

    # Get the last modification time for the target file
    targetfile_time = os.path.getmtime(targetfile)

    # Compare the modification times
    for sourcefile in sourcefiles:
        if os.path.exists(sourcefile) and \
            os.path.getmtime(sourcefile) > targetfile_time:
            return True

    # If none of the source files are newer, return False
    return False



def create_zip_archive(target: str) -> None:
    """ Create a ZIP archive of the output file """
    target_dir = os.path.dirname(target)
    target_filename, _ = os.path.splitext(os.path.basename(target))
    target_assets_dir = os.path.join(target_dir, target_filename)
    zip_file = os.path.join(target_dir, target_filename + ".zip")
    intermediate_file = zip_file.replace('.zip', '.md')
    imsmanifest_file = zip_file.replace('.zip', '.xml')
    logger.info("Creating ZIP archive: %s ...", zip_file)
    # Create a ZipFile object in WRITE mode
    with zipfile.ZipFile(zip_file, 'w') as zipf:
        # Add target file to the zip file
        zipf.write(target, os.path.basename(target))
        zipf.write(intermediate_file, os.path.basename(intermediate_file))
        if os.path.exists(imsmanifest_file):
            zipf.write(imsmanifest_file, "imsmanifest.xml")
        # Add files from the target assets directory to the zip file
        for foldername, _, filenames in os.walk(target_assets_dir):
            for filename in filenames:
                # create complete filepath of file in directory
                filepath = os.path.join(foldername, filename)
                # Add file to zip
                zipf.write(filepath, os.path.relpath(filepath, start=target_dir))
        # Add generation scripts to the zip file
        generate_file = os.path.join(MARKSLIDE_DIR, 'generate.sh')
        zipf.write(generate_file, os.path.relpath(generate_file, start=MARKSLIDE_DIR))
        setup_file = os.path.join(MARKSLIDE_DIR, 'setup.sh')
        zipf.write(setup_file, os.path.relpath(setup_file, start=MARKSLIDE_DIR))


def generate(source: str, target: str, options: list|None = None) -> bool:
    """ Generate a PDF, PPTX or HTML file from a Markdown file using Marp. """
    # Check if the source file exists and is readable
    if os.access(source, os.R_OK):
        logger.debug("Processing file: %s", source)
        logger.debug("Generating file: %s ...", target)
        subprocess.run([NPX_CMD, "marp", "--html",
        "--pdf-outlines", "--pdf-outlines.pages=false",
        "--pdf-notes", "--allow-local-files", source, "-o", target], check=True)

        if options and "--zip" in options:
            create_zip_archive(target)
    else:
        logger.warning("Source file %s not found or is not readable", source)
        return False

    return True


if __name__ == "__main__":
    # Check if two arguments were provided
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <input-file.md> <output-file.?> [options]")
        print("Options: --zip")
        sys.exit(0)

    find_template_directory()

    # Path to the YAML file
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    if len(sys.argv) > 3:
        generate(input_file, output_file, sys.argv[3:])
    else:
        generate(input_file, output_file)
