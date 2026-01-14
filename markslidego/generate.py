#!/usr/bin/env python3
""" Generate slides (as PDF, PPTX or HTML files) from Markdown files using Marp. """
import re
import os
import sys
import subprocess
import logging
import zipfile
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


def create_ims_manifest(target_file: str, course: str, course_title: str, title: str) -> None:
    """ Create imsmanifest.xml and zip file for SCORM """
    target_rel = os.path.basename(target_file)
    zip_file, _ = os.path.splitext(target_file)
    zip_file += ".zip"
    manifest_file, _ = os.path.splitext(target_file)
    manifest_file += ".xml"
    course_title = course_title.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    title = title.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    logger.info("Creating SCORM manifest: %s ...", manifest_file)
    content = f"""<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="{course}Manifest" xmlns="http://www.imsglobal.org/xsd/imscp_v1p1">
  <organizations default="{course}">
    <organization identifier="{course}">
      <title>{course_title}</title>
      <item identifier="ITEM-1" identifierref="RES-1">
        <title>{title}</title>
      </item>
    </organization>
  </organizations>
  <resources>
    <resource identifier="RES-1" type="webcontent" href="{target_rel}">
      <file href="{target_rel}" />
    </resource>
  </resources>
</manifest>
"""
    with open(manifest_file, 'w', encoding="utf-8") as file:
        file.write(content)



def copy_file_with_assets(source_file:str, dest_file:str) -> None:
    """ Copy a Markdown file and its assets (images, etc.) to another location. """
    # copy the source_file to the dest_file
    if os.path.exists(source_file):
        os.makedirs(os.path.dirname(dest_file), exist_ok=True)
        with open(source_file, 'r', encoding="utf-8") as src_file:
            with open(dest_file, 'w', encoding="utf-8") as dst_file:
                dst_file.write(src_file.read())
    else:
        print(f"Warning: Provided file {source_file} does not exist.")

    # copy the provided file sub-directory (images, etc.) to the intermediate file sub-directory
    source_file_dir = source_file.replace('.md', '')
    if os.path.exists(source_file_dir):
        dest_file_dir = dest_file.replace('.md', '')
        os.makedirs(dest_file_dir, exist_ok=True)
        os.system(f"cp -r {source_file_dir}/* {dest_file_dir}")



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

        if options:
            if "--zip" in options or "--scorm" in options:
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

    # Path to the YAML file
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    if len(sys.argv) > 3:
        generate(input_file, output_file, sys.argv[3:])
    else:
        generate(input_file, output_file)
