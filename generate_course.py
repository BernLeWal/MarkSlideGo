#!/usr/bin/env python3
""" Generate the slide decks for a course from a YAML file. """
import os
import sys
import yaml
import zipfile
from tqdm.autonotebook import tqdm
from generate import find_template_directory, generate, preprocess, preprocess_multiple, is_source_newer, is_any_source_newer
from generate_questions import generate_questions


def copy_file_with_assets(intermediate_file):
    provided_file = intermediate_file.replace('output/', 'moodle/')

    # copy the provided file to the intermediate file
    if os.path.exists(provided_file):
        os.makedirs(os.path.dirname(intermediate_file), exist_ok=True)
        with open(provided_file, 'r', encoding="utf-8") as src_file:
            with open(intermediate_file, 'w', encoding="utf-8") as dst_file:
                dst_file.write(src_file.read())
    else:
        print(f"Warning: Provided file {provided_file} does not exist.")

    # copy the provided file sub-directory (images, etc.) to the intermediate file sub-directory
    provided_file_dir = provided_file.replace('.md', '')
    if os.path.exists(provided_file_dir):
        intermediate_file_dir = intermediate_file.replace('.md', '')
        os.makedirs(intermediate_file_dir, exist_ok=True)
        os.system(f"cp -r {provided_file_dir}/* {intermediate_file_dir}")


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
                source_file = "../../../catalogs/" + slides[j]['source']
                if is_source_newer(source_file, intermediate_file):
                    preprocess(source_file, intermediate_file, placeholders)

            if 'sources' in slides[j]:
                source_files = []
                for source in slides[j]['sources']:
                    source_files.append("../../../catalogs/" + source)
                if is_any_source_newer(source_files, intermediate_file):
                    preprocess_multiple(source_files, intermediate_file, placeholders)

            if target_file != intermediate_file:
                if not os.path.exists(intermediate_file):
                    # Use provided source from repo, so no preprocessing needed                    
                    copy_file_with_assets(intermediate_file)

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
        print(f"- generate complete course BIF3/SWEN1:  {script_file} fhtw/bif3_swen1")
        print(f"- generate specific topic SS-A:         {script_file} fhtw/bif3_swen1 SS-A")
        print(f"- generate specific markdown file:      {script_file} fhtw/bif3_swen1 Class-1 java-kickstart.md")
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
        copy_file_with_assets(f"output/{topic}/{md_file}")

        # Generate the slidedeck PDF
        target_file = f"output/{topic}/{md_file}".replace('.md', '.pdf')
        output_count += generate(f"output/{topic}/{md_file}", target_file)

        # Generate the HTML ZIP SCORM package
        target_file = f"output/{topic}/{md_file}".replace('.md', '.html')
        create_ims_manifest(target_file, course_name, course_name, md_file.replace('.md', ''))
        output_count += generate(f"output/{topic}/{md_file}", target_file, ['--zip', '--scorm'])


    print(f"Generated {output_count} slide decks.")
