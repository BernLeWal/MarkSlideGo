#!/usr/bin/env python3

import os
import sys

from markslidego.markdown.reader import MarkdownReader
from markslidego.moodle.backup import MoodleBackup


# ------------------- Main Program -------------------
if __name__ == "__main__":
    # Check if one argument was provided
    if len(sys.argv) < 2:
        script_file = os.path.basename(sys.argv[0])
        print(f"Usage: {script_file} <course> [<topic>] [<md_file>] ")
        print("Examples (using the courses-repo of bif3-swen1):")
        print(f"- generate complete course BIF3/SWEN1:  {script_file} bif3-swen1")
        print(f"- generate specific topic SS-A:         {script_file} bif3-swen1 SS-A")
        print(f"- generate specific markdown file:      {script_file} bif3-swen1 Class-1 java-kickstart.md")
        sys.exit(0)

    # Path to the course
    course = sys.argv[1]
    course_name = os.path.basename(course)
    course_path = os.path.join("courses", course)
    if not os.path.exists(course_path):
        print(f"Error: Course {course_path} does not exist.")
        sys.exit(1)
    if not os.path.isdir(course_path):
        print(f"Error: Course {course_path} is not a directory.")
        sys.exit(1)

    filter_topic_name = None
    if len(sys.argv) > 2:
        filter_topic_name = sys.argv[2]
    if filter_topic_name == "." or filter_topic_name == "*" or filter_topic_name == "":
        filter_topic_name = None

    filter_md_file = None
    if len(sys.argv) > 3:
        filter_md_file = sys.argv[3]
    if filter_md_file == "." or filter_md_file == "*" or filter_md_file == "":
        filter_md_file = None

    # Change into course-directory 
    project_root = os.path.dirname(os.path.abspath(__file__))
    course_dir = os.path.dirname(course_path)
    os.chdir(course_path)

    course_name = os.path.basename(course_path)
    course_title = course_name.replace("-", " ").title()
    # if README.md exists, use the first line as course name
    course_info = MarkdownReader.get_md_info("README.md")
    if course_info is not None and 'title' in course_info:
        course_title = course_info['title']
    print(f"Generating course '{course_title}' from {course_path}:")
    generator = MoodleBackup(course_name, course_title, 1)

    # collect all .md files in the course_path recursively
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".md"):
                if filter_md_file is not None and file != filter_md_file:
                    continue

                md_filepath = os.path.join(root, file).replace("\\", "/").lstrip("./") 
                md_file = MarkdownReader(md_filepath)
                if md_file.metadata is None:
                    continue
                
                topic_name = os.path.dirname(md_filepath)
                if topic_name is None or topic_name == "":
                    topic_name = os.path.basename(md_filepath).replace(".md", "")
                if filter_topic_name is not None and topic_name != filter_topic_name:
                    continue
                topic_nr = int(md_file.metadata.get('section_number', "0"))
                print(f"- {md_filepath}: topic_name={topic_name}, topic_nr={topic_nr}")

                section = generator.sections[topic_name] if topic_name in generator.sections else None
                if section is None:
                    section = generator.create_section(md_filepath, topic_name, topic_nr)

                if md_file.is_marp:
                    activity_title = md_file.metadata['title'] if 'title' in md_file.metadata else os.path.basename(md_filepath).replace(".md", "").replace("-", " ").title()
                    generator.create_activity_scorm(section, activity_title, md_filepath.replace(".md", ".html"), md_filepath)
                    generator.create_activity_file(section, activity_title + " (PDF)", md_filepath.replace(".md", ".pdf"), md_filepath)
                    
                if md_file.is_moodle:
                    generator.create_activity_lesson(section, md_file)



    # Generate the moodle backup .mbz file
    generator.generate_mbz(course_name + ".mbz", remove_intermediate_files=False, replace_existing=True)
    generator.generate_zip(course_name + ".zip", remove_intermediate_files=False, replace_existing=True)
