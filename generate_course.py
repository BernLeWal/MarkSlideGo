#!/usr/bin/env python3
""" Generate the slide decks for a course from a YAML file. """
import logging
import os
import re
import sys
import shutil
from dotenv import load_dotenv
import yaml
import zipfile
from tqdm.autonotebook import tqdm
from generate import copy_file_with_assets, create_ims_manifest, generate, is_source_newer, is_any_source_newer
from generate_questions import generate_questions


load_dotenv()  # take environment variables from .env.

# Setup logging
LOGGING_LEVEL = os.environ.get('LOGGING_LEVEL', 'INFO')  # default to INFO if no env var set
numeric_level = getattr(logging, LOGGING_LEVEL.upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError(f'Invalid log level: {LOGGING_LEVEL}')
logging.basicConfig(level=numeric_level)
logger = logging.getLogger(__name__)

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


def copy_assets_to_output(content: str, source_file: str, target_file: str) -> str:
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
        logger.warning("Source file %s not found or not readable, skipping generation of %s", source_file,target_file)



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
    failed = False

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
            failed = True

    if failed:
        logger.warning("Source file(s) not found, skipping generation of %s", target_file)
        return
    
    # Build the complete content
    toc += "\n---\n"
    content = template + toc + content

    # Replace the placeholders in the content
    for key, value in placeholders.items():
        content = content.replace('{{' + key + '}}', value)

    logger.debug("Generating file: %s ...", target_file)
    with open(target_file, 'w', encoding="utf-8") as file:
        file.write(content)


def generate_course_topic(name, data_topic, course_title, data_course, placeholders, md_file=None) -> int:
    """ Create a subdirectory for the topic """

    # Extract the slides data
    slides = data_topic['slides']
    slides_count = len(slides)
    output_count = 0

    # Iterate through each slide
    for j in tqdm(range(slides_count), unit="slide", desc=f"Processing slides for {name}"):
        #print(data_topic['slides'][j]['source'])
        # Extract the source and target for each slide
        placeholders['title'] = slides[j]['title']
        if slides[j]['target'].endswith('.md'):
            target_file = "output/" + name + "/" + slides[j]['target']
            intermediate_file = target_file
        else:
            target_file = "output/" + name + "/" + slides[j]['target']
            intermediate_file, _ = os.path.splitext(target_file)
            intermediate_file += ".md"

        # Preprocess the source_file(s), replace placeholders
        if md_file is None or md_file == os.path.basename(intermediate_file):
            os.makedirs(f"output/{name}", exist_ok=True)

            if 'source' in slides[j]:
                source_file = "../../catalogs/" + slides[j]['source']
                if is_source_newer(source_file, intermediate_file):
                    preprocess(source_file, intermediate_file, placeholders)

            if 'sources' in slides[j]:
                source_files = []
                for source in slides[j]['sources']:
                    source_files.append("../../catalogs/" + source)
                if is_any_source_newer(source_files, intermediate_file):
                    preprocess_multiple(source_files, intermediate_file, placeholders)

            if target_file != intermediate_file:
                if not os.path.exists(intermediate_file):
                    # Use provided source from repo, so no preprocessing needed    
                    provided_file = intermediate_file.replace('output/', 'moodle/')
                    copy_file_with_assets(provided_file, intermediate_file)

        # Generate the slidedeck
        if target_file != intermediate_file:
            if is_source_newer(intermediate_file, target_file):
                # Provide generation options
                if 'options' in slides[j]:
                    options = slides[j]['options'].split(" ")
                    if '--scorm' in options:
                        create_ims_manifest(target_file,
                        data_course, course_title, placeholders['title'])
                else:
                    options = None

                if md_file is None or md_file == os.path.basename(intermediate_file):
                    if generate(intermediate_file, target_file, options):
                        output_count += 1

        # Generate questions
        if 'questions' in slides[j]:
            questions = slides[j]['questions']
            questions_file, _ = os.path.splitext(target_file)
            questions_file += ".csv"
            if not os.path.exists(questions_file):
                generate_questions(placeholders['title'], slides[j]['title'], intermediate_file, int(questions), questions_file)

    return output_count


def generate_course(yaml_file: str, topic: str|None = None, md_file: str|None = None) -> int:
    """ Generate the slide decks for a course from a YAML file. """
    # Load YAML file
    with open(yaml_file, 'r', encoding="utf-8") as file:
        data = yaml.safe_load(file)

    # Read the number of topics
    topics_count = len(data['topics'])
    placeholders = {}
    placeholders['course-title'] = data['course-title']
    placeholders['course'] = data['course']
    placeholders['program'] = data['program']
    placeholders['version'] = data['version']
    output_count = 0

    # Iterate through each topic
    for i in tqdm(range(topics_count), unit="topic", desc=f"Processing topics of {yaml_file}"):
        # Extract the name for each topic
        course_title = data['course-title']
        data_course = data['course']
        data_topic = data['topics'][i]
        name = data_topic['name']

        # If a specific topic is provided, skip others
        if topic is not None and name != topic:
            continue

        output_count += generate_course_topic(name, data_topic, course_title, data_course, placeholders, md_file)

        # if topic specified, then create a zip file of the topic
        if topic is not None:
            topic_output_dir = os.path.abspath(f"output/{topic}")
            zip_file = os.path.join(topic_output_dir, "..", f"{topic}.zip")
            if os.path.exists(zip_file):
                os.remove(zip_file)
            try:
                with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in os.walk(topic_output_dir):
                        for file in files:
                            if file == f"{topic}.zip":
                                continue  # Don't include the zip file itself
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, topic_output_dir)
                            zipf.write(file_path, arcname)        
            except Exception as e:
                print(f"Error creating zip file {zip_file}: {e}")

    # if topic is not specified, then create a zip file of the course
    if topic is None:
        course_output_dir = os.path.abspath("output")
        zip_file = os.path.join(course_output_dir, os.path.basename(yaml_file).replace(".yml", ".zip"))
        if os.path.exists(zip_file):
            os.remove(zip_file)
        try:
            with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(course_output_dir):
                    for file in files:
                        if file == os.path.basename(zip_file):
                            continue  # Don't include the zip file itself
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, course_output_dir)
                        zipf.write(file_path, arcname)        
        except Exception as e:
            print(f"Error creating zip file {zip_file}: {e}")


    return output_count


if __name__ == "__main__":
    # Check if one argument was provided
    if len(sys.argv) < 2:
        script_file = os.path.basename(sys.argv[0])
        print(f"Usage: {script_file} <course> [<topic>] [<md_file>] ")
        print("Examples (using the courses-repo of fhtw):")
        print(f"- generate complete course BIF3/SWEN1:  {script_file} bif3-swen1")
        print(f"- generate specific topic SS-A:         {script_file} bif3-swen1 SS-A")
        print(f"- generate specific markdown file:      {script_file} bif3-swen1 Class-1 java-kickstart.md")
        sys.exit(0)

    # Path to the YAML file
    course = sys.argv[1]
    course_name = os.path.basename(course)
    course_path = os.path.join("courses", course, f"{course_name}.yml")
    if not os.path.exists(course_path):
        print(f"Error: Course file {course_path} does not exist.")
        sys.exit(1)

    topic = None
    if len(sys.argv) > 2:
        topic = sys.argv[2]
    if topic == "." or topic == "*" or topic == "":
        topic = None

    md_file = None
    if len(sys.argv) > 3:
        md_file = sys.argv[3]
    if md_file == "." or md_file == "*" or md_file == "":
        md_file = None

    # Change into course-directory and generate the course
    os.chdir(os.path.dirname(course_path))
    find_template_directory()
    output_count = generate_course(os.path.basename(course_path), topic, md_file)

    if output_count == 0 and topic is not None and md_file is not None:
        # The md_file is not in the yaml file yet, so generate this one manually
        os.makedirs(f"output/{topic}", exist_ok=True)

        source_file = f"moodle/{topic}/{md_file}"
        dest_file = f"output/{topic}/{md_file}"
        source_file = dest_file.replace('output/', 'moodle/')
        copy_file_with_assets(source_file, dest_file)

        # Generate the slidedeck PDF
        target_file = f"output/{topic}/{md_file}".replace('.md', '.pdf')
        output_count += generate(f"output/{topic}/{md_file}", target_file)

        # Generate the HTML ZIP SCORM package
        target_file = f"output/{topic}/{md_file}".replace('.md', '.html')
        create_ims_manifest(target_file, course_name, course_name, md_file.replace('.md', ''))
        output_count += generate(f"output/{topic}/{md_file}", target_file, ['--zip', '--scorm'])


    print(f"Generated {output_count} items.")
