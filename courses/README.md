# MarkSlide Go - Courses

Place all your course-definition files in the form of hiearchically organized yaml configuration-files into the courses/ directory.
They will be used for the slide generator- and tool-scripts.

## Generate Slides for a course

* In create a sub-dir for each (e.g. moodle) course.
* Inside the sub-directories there are YAML-files, containing the course-structure filled with the slides-config per topic.

To generate all the slides for a moodle-course move inside the specific course-directory, and execute the following command:

```shell
$ python3 generate_course.py <coursefile>.yml
```

The output will be stored in the corresponding output/ subdirectory.

## YAML file format

Finde here a JSON Schema representation of the YAML file format:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "course-title": {
      "type": "string",
      "description": "Title of the course"
    },
    "course": {
      "type": "string",
      "description": "Short course code"
    },
    "program": {
      "type": "string",
      "description": "Program or degree abbreviation"
    },
    "version": {
      "type": "string",
      "description": "Version of the configuration file"
    },
    "topics": {
      "type": "array",
      "description": "List of topics in the course",
      "items": {
        "type": "object",
        "properties": {
          "name": {
            "type": "string",
            "description": "Topic name or identifier"
          },
          "title": {
            "type": "string",
            "description": "Title of the topic"
          },
          "slides": {
            "type": "array",
            "description": "List of slides for the topic",
            "items": {
              "type": "object",
              "properties": {
                "title": {
                  "type": "string",
                  "description": "Title of the slide"
                },
                "source": {
                  "type": ["string", "null"],
                  "description": "Source file for the slide (single file)"
                },
                "sources": {
                  "type": ["array", "null"],
                  "description": "Source files for the slide (multiple files)",
                  "items": {
                    "type": "string"
                  }
                },
                "target": {
                  "type": "string",
                  "description": "Output target file for the slide. The following suffixes are supported: .html, .pdf and .pptx"
                },
                "options": {
                  "type": ["string", "null"],
                  "description": "Optional settings for the slide, one of: --zip, --scorm"
                },
                "questions": {
                  "type": ["integer", "null"],
                  "description": "Number of questions to generate associated with the slide (requires OpenAI key in .env file)"
                }
              },
              "required": ["title", "target"],
              "oneOf": [
                {
                  "required": ["source"]
                },
                {
                  "required": ["sources"]
                }
              ]
            }
          }
        },
        "required": ["name", "title", "slides"]
      }
    }
  },
  "required": ["course-title", "course", "program", "version", "topics"]
}

```