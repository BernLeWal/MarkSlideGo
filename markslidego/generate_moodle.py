#!/usr/bin/env python3

import os
import sys

from markslidego.markdown_utils import get_md_info
from markslidego.moodle.backup import MoodleBackup
from markslidego.markdown_utils import get_marp_info


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
    course_info = get_md_info("README.md")
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

                md_file = os.path.join(root, file).replace("\\", "/").lstrip("./") 
                marp_info = get_marp_info(md_file)
                if marp_info is None:
                    continue
                
                topic_name = os.path.dirname(md_file)
                if topic_name is None or topic_name == "":
                    topic_name = os.path.basename(md_file).replace(".md", "")
                if filter_topic_name is not None and topic_name != filter_topic_name:
                    continue
                print(f"- {md_file}: topic_name={topic_name}")

                section = generator.sections[topic_name] if topic_name in generator.sections else None
                if section is None:
                    section = generator.create_section(md_file, topic_name)

                activity_title = marp_info['title'] if 'title' in marp_info else os.path.basename(md_file).replace(".md", "").replace("-", " ").title()
                generator.create_activity(section, activity_title, md_file.replace(".md", ".html"), md_file, "--scorm")
                generator.create_activity(section, activity_title + " (PDF)", md_file.replace(".md", ".pdf"), md_file, None)



    # Generate the moodle backup .mbz file
    generator.generate_mbz(course_name + ".mbz", removeIntermediateFiles=False, replaceExisting=True)
    generator.generate_zip(course_name + ".zip", removeIntermediateFiles=False, replaceExisting=True)
