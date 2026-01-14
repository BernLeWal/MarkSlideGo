from markslidego.moodle.base import MoodleBase


import os


class MoodleSection(MoodleBase):

    next_section_id = 30000

    def __init__(self, name:str, title:str, number:int):
        super().__init__()
        self.id = MoodleSection.next_section_id
        MoodleSection.next_section_id += 1
        self.name = name
        self.title = title.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        self.number = number
        self.summary = ""

        self.activities = []


    def generate_section(self) -> None:
        file_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<section id="{self.id}">
  <number>{self.number}</number>
  <name>{self.title}</name>
  <summary>{self.summary.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')}</summary>
  <summaryformat>1</summaryformat>
  <sequence>728313,1956075,1956077,1956079,1956080,1661072,1661187,678060,728279,728280,1992663</sequence>
  <visible>1</visible>
  <availabilityjson>{'{"op":"&amp;","c":[],"showc":[]}'}</availabilityjson>
  <component>$@NULL@$</component>
  <itemid>$@NULL@$</itemid>
  <timemodified>{self.current_timestamp}</timemodified>
  <course_format_options id="163054">
    <format>scfhtw</format>
    <name>blockname</name>
    <value></value>
  </course_format_options>
  <course_format_options id="163055">
    <format>scfhtw</format>
    <name>sectionblock</name>
    <value>0</value>
  </course_format_options>
  <course_format_options id="163056">
    <format>scfhtw</format>
    <name>sectionstartdate</name>
    <value>0</value>
  </course_format_options>
  <course_format_options id="163057">
    <format>scfhtw</format>
    <name>sectiontype</name>
    <value>0</value>
  </course_format_options>
</section>
"""
        with open(f"section.xml", "w", encoding="utf-8") as f:
            f.write(file_content)


    def generate(self) -> None:
        os.makedirs(f"section_{self.id}", exist_ok=True)
        os.chdir(f"section_{self.id}")

        self.generate_empty("inforef.xml", "inforef")
        self.generate_section()

        os.chdir("..")