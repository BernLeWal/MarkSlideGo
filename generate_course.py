#!/usr/bin/env python3
""" Generate the slide decks for a course from a YAML file. """
import os
import sys
import yaml
from tqdm.autonotebook import tqdm
from generate import generate, preprocess, preprocess_multiple, is_source_newer, is_any_source_newer
from generate_questions import generate_questions


def create_ims_manifest(target_file: str, course: str, course_title: str, title: str) -> None:
    """ Create imsmanifest.xml and zip file for SCORM """
    target_rel = os.path.basename(target_file)
    zip_file, _ = os.path.splitext(target_file)
    zip_file += ".zip"
    manifest_file, _ = os.path.splitext(target_file)
    manifest_file += ".xml"
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


def generate_course_topic(name, data_topic, course_title, data_course, placeholders):
    """ Create a subdirectory for the topic """
    #print(f"Creating directory: {name}")
    os.makedirs(f"output/{name}", exist_ok=True)

    # Extract the slides data
    slides = data_topic['slides']
    slides_count = len(slides)

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

        if 'source' in slides[j]:
            source_file = "../../../catalogs/" + slides[j]['source']
            if is_source_newer(source_file, intermediate_file):
                # Preprocess the source_file, replace placeholders
                preprocess(source_file, intermediate_file, placeholders)

        if 'sources' in slides[j]:
            source_files = []
            for source in slides[j]['sources']:
                source_files.append("../../../catalogs/" + source)
            if is_any_source_newer(source_files, intermediate_file):
                # Preprocess the source files, replace placeholders
                preprocess_multiple(source_files, intermediate_file, placeholders)

        # Generate the slidedeck
        if target_file != intermediate_file and is_source_newer(intermediate_file, target_file):
            # Provide generation options
            if 'options' in slides[j]:
                options = slides[j]['options'].split(" ")
                if '--scorm' in options:
                    create_ims_manifest(target_file,
                    data_course, course_title, placeholders['title'])
            else:
                options = None

            generate(intermediate_file, target_file, options)

        # Generate questions
        if 'questions' in slides[j]:
            questions = slides[j]['questions']
            questions_file, _ = os.path.splitext(target_file)
            questions_file += ".csv"
            if not os.path.exists(questions_file):
                generate_questions(placeholders['title'], slides[j]['title'], intermediate_file, int(questions), questions_file)


def generate_course(yaml_file: str) -> None:
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

    # Iterate through each topic
    for i in tqdm(range(topics_count), unit="topic", desc=f"Processing topics of {yaml_file}"):
        # Extract the name for each topic
        course_title = data['course-title']
        data_course = data['course']
        data_topic = data['topics'][i]
        name = data_topic['name']

        generate_course_topic(name, data_topic, course_title, data_course, placeholders)


if __name__ == "__main__":
    # Check if one argument was provided
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <course-file.yml>")
        sys.exit(0)

    # Path to the YAML file
    course_file = sys.argv[1]
    generate_course(course_file)
