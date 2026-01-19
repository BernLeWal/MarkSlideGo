"""
Moodle activity representation for Moodle backup structure.
Provides methods to generate XML entries for Moodle activities in the backup.
"""
import os
from typing import override
from markslidego.markdown.reader import MarkdownReader
from markslidego.moodle.base import MoodleBase
from markslidego.moodle.file import MoodleFile
from markslidego.moodle.section import MoodleSection


class MoodleActivity(MoodleBase):
    """ Class to represent a Moodle activity in the backup structure. """

    next_activity_id = 20000
    next_module_id = 25000
    next_lesson_page_id = 36000
    next_lesson_answer_id = 69000

    def __init__(self, name:str, title:str, modulename:str="resource", lesson_md: MarkdownReader| None = None):
        super().__init__()
        self.id = MoodleActivity.next_activity_id
        MoodleActivity.next_activity_id += 1
        self.module_id = MoodleActivity.next_module_id
        MoodleActivity.next_module_id += 1
        self.name = name
        self.title = title.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        self.modulename = modulename
        self.lesson_md = lesson_md

        self.files:list[MoodleFile] = []
        self.section: MoodleSection | None = None


    def __generate_inforef__(self) -> None:
        file_content = """<?xml version="1.0" encoding="UTF-8"?>
<inforef>
  <fileref>
"""
        for f in self.files:
            file_content += f"""    <file>
      <id>{f.file_id}</id>
    </file>
"""
        file_content += """  </fileref>
</inforef>
"""
        with open("inforef.xml", "w", encoding="utf-8") as f:
            f.write(file_content)


    def __generate_module__(self) -> None:
        file_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<module id="{self.module_id}" version="2024100700">
  <modulename>{self.modulename}</modulename>
  <sectionid>{self.section.id if self.section else 0}</sectionid>
  <sectionnumber>{self.section.number if self.section else 0}</sectionnumber>
  <idnumber>$@NULL@$</idnumber>
  <added>{self.current_timestamp}</added>
  <score>0</score>
  <indent>1</indent>
  <visible>1</visible>
  <visibleoncoursepage>1</visibleoncoursepage>
  <visibleold>1</visibleold>
  <groupmode>0</groupmode>
  <groupingid>0</groupingid>
  <completion>0</completion>
  <completiongradeitemnumber>$@NULL@$</completiongradeitemnumber>
  <completionpassgrade>0</completionpassgrade>
  <completionview>0</completionview>
  <completionexpected>0</completionexpected>
  <availability>$@NULL@$</availability>
  <showdescription>0</showdescription>
  <downloadcontent>1</downloadcontent>
  <lang>$@NULL@$</lang>
  <plugin_plagiarism_turnitinsim_module>
    <turnitinsim_mods>
    </turnitinsim_mods>
  </plugin_plagiarism_turnitinsim_module>
  <tags>
  </tags>
</module>
"""
        with open("module.xml", "w", encoding="utf-8") as f:
            f.write(file_content)


    def __generate_resource__(self) -> None:
        file_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<activity id="{self.id}" moduleid="{self.module_id}" modulename="resource" contextid="{self.files[0].context_id if self.files else 0}">
  <resource id="{self.id}">
    <name>{self.title}</name>
    <intro></intro>
    <introformat>1</introformat>
    <tobemigrated>0</tobemigrated>
    <legacyfiles>0</legacyfiles>
    <legacyfileslast>$@NULL@$</legacyfileslast>
    <display>0</display>
    <displayoptions>a:1:{"{s:10:\"printintro\";i:1;}"}</displayoptions>
    <filterfiles>0</filterfiles>
    <revision>0</revision>
    <timemodified>{self.current_timestamp}</timemodified>
  </resource>
</activity>
"""
        with open("resource.xml", "w", encoding="utf-8") as f:
            f.write(file_content)


    def __generate_scorm__(self) -> None:
        # find the imsmanifest.xml file in self.files
        imsmanifest_file = next((f for f in self.files if f.filename == "imsmanifest.xml"), None)
        scormzip_file = self.files[-1] if self.files else None

        file_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<activity id="{self.id}" moduleid="{self.module_id}" modulename="scorm" contextid="{self.files[0].context_id if self.files else 0}">
  <scorm id="{self.id}">
    <name>{self.title}</name>
    <scormtype>local</scormtype>
    <reference>{scormzip_file.filename if scormzip_file else ''}</reference>
    <intro></intro>
    <introformat>0</introformat>
    <version>SCORM_1.2</version>
    <maxgrade>100</maxgrade>
    <grademethod>1</grademethod>
    <whatgrade>0</whatgrade>
    <maxattempt>0</maxattempt>
    <forcecompleted>0</forcecompleted>
    <forcenewattempt>0</forcenewattempt>
    <lastattemptlock>0</lastattemptlock>
    <masteryoverride>1</masteryoverride>
    <displayattemptstatus>1</displayattemptstatus>
    <displaycoursestructure>0</displaycoursestructure>
    <updatefreq>0</updatefreq>
    <sha1hash>{scormzip_file.content_hash if scormzip_file else ''}</sha1hash>
    <md5hash></md5hash>
    <revision>1</revision>
    <launch>3641</launch>
    <skipview>0</skipview>
    <hidebrowse>0</hidebrowse>
    <hidetoc>1</hidetoc>
    <nav>1</nav>
    <navpositionleft>-100</navpositionleft>
    <navpositiontop>-100</navpositiontop>
    <auto>0</auto>
    <popup>0</popup>
    <options></options>
    <width>100</width>
    <height>500</height>
    <timeopen>0</timeopen>
    <timeclose>0</timeclose>
    <timemodified>1755603996</timemodified>
    <completionstatusrequired>$@NULL@$</completionstatusrequired>
    <completionscorerequired>$@NULL@$</completionscorerequired>
    <completionstatusallscos>0</completionstatusallscos>
    <autocommit>0</autocommit>
    <scoes>
      <sco id="{self.id}0">
        <manifest>{imsmanifest_file.content_dict['manifest.identifier'] if imsmanifest_file else ''}</manifest>
        <organization></organization>
        <parent>/</parent>
        <identifier>{imsmanifest_file.content_dict['organization.identifier'] if imsmanifest_file else ''}</identifier>
        <launch></launch>
        <scormtype></scormtype>
        <title>{imsmanifest_file.content_dict['organization.title'] if imsmanifest_file else ''}</title>
        <sortorder>1</sortorder>
        <sco_datas>
        </sco_datas>
        <seq_ruleconds>
        </seq_ruleconds>
        <seq_rolluprules>
        </seq_rolluprules>
        <seq_objectives>
        </seq_objectives>
        <sco_tracks>
        </sco_tracks>
      </sco>
      <sco id="{self.id}1">
        <manifest>{imsmanifest_file.content_dict['manifest.identifier'] if imsmanifest_file else ''}</manifest>
        <organization>{imsmanifest_file.content_dict['organization.identifier'] if imsmanifest_file else ''}</organization>
        <parent>{imsmanifest_file.content_dict['organization.identifier'] if imsmanifest_file else ''}</parent>
        <identifier>{imsmanifest_file.content_dict['item.identifier'] if imsmanifest_file else ''}</identifier>
        <launch>{imsmanifest_file.content_dict['resource.href'] if imsmanifest_file else ''}</launch>
        <scormtype>asset</scormtype>
        <title>{imsmanifest_file.content_dict['item.title'] if imsmanifest_file else ''}</title>
        <sortorder>2</sortorder>
        <sco_datas>
          <sco_data id="{self.id}2">
            <name>isvisible</name>
            <value>true</value>
          </sco_data>
          <sco_data id="{self.id}3">
            <name>parameters</name>
            <value></value>
          </sco_data>
        </sco_datas>
        <seq_ruleconds>
        </seq_ruleconds>
        <seq_rolluprules>
        </seq_rolluprules>
        <seq_objectives>
        </seq_objectives>
        <sco_tracks>
        </sco_tracks>
      </sco>
    </scoes>
  </scorm>
</activity>
"""
        with open("scorm.xml", "w", encoding="utf-8") as f:
            f.write(file_content)


    def __generate_lesson__(self) -> None:
        file_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<activity id="{self.id}" moduleid="{self.module_id}" modulename="lesson" contextid="{self.files[0].context_id if self.files else 0}">
  <lesson id="{self.id}">
    <course>25041</course>
    <name>{self.title}</name>
    <intro></intro>
    <introformat>1</introformat>
    <practice>0</practice>
    <modattempts>0</modattempts>
    <usepassword>0</usepassword>
    <password></password>
    <dependency>0</dependency>
    <conditions>O:8:"stdClass":3:{"{s:9:\"timespent\";i:0;s:9:\"completed\";i:0;s:15:\"gradebetterthan\";i:0;}"}</conditions>
    <grade>10</grade>
    <custom>1</custom>
    <ongoing>0</ongoing>
    <usemaxgrade>0</usemaxgrade>
    <maxanswers>4</maxanswers>
    <maxattempts>1</maxattempts>
    <review>0</review>
    <nextpagedefault>0</nextpagedefault>
    <feedback>0</feedback>
    <minquestions>0</minquestions>
    <maxpages>1</maxpages>
    <timelimit>0</timelimit>
    <retake>0</retake>
    <activitylink>0</activitylink>
    <mediafile></mediafile>
    <mediaheight>480</mediaheight>
    <mediawidth>640</mediawidth>
    <mediaclose>0</mediaclose>
    <slideshow>0</slideshow>
    <width>640</width>
    <height>480</height>
    <bgcolor>#FFFFFF</bgcolor>
    <displayleft>1</displayleft>
    <displayleftif>0</displayleftif>
    <progressbar>1</progressbar>
    <available>0</available>
    <deadline>0</deadline>
    <timemodified>{self.current_timestamp}</timemodified>
    <completionendreached>0</completionendreached>
    <completiontimespent>0</completiontimespent>
    <allowofflineattempts>0</allowofflineattempts>
    <pages>
"""
        if self.lesson_md:
            for idx, page in enumerate(self.lesson_md.pages):
                page_id = MoodleActivity.next_lesson_page_id + idx*10
                if page.moodle_type == "ESSAY":
                    qtype = 10
                elif page.moodle_type == "SHORTANSWER":
                    qtype = 1
                elif page.moodle_type == "TRUEFALSE":
                    qtype = 2
                else: # CONTENT
                    qtype = 20
                page_content = f"""      <page id="{page_id}">
        <prevpageid>{page_id-10 if idx > 0 else 0}</prevpageid>
        <nextpageid>{page_id + 10}</nextpageid>
        <qtype>{qtype}</qtype>
        <qoption>0</qoption>
        <layout>1</layout>
        <display>1</display>
        <timecreated>{self.current_timestamp}</timecreated>
        <timemodified>{self.current_timestamp}</timemodified>
        <title>{page.title}</title>
        <contents>{page.html_to_xml(page.to_html(page.strip()))}</contents>
        <contentsformat>1</contentsformat>
        <answers>
"""
                for answer_idx, answer in enumerate(page.moodle_links):
                    answer_content = f"""          <answer id="{MoodleActivity.next_lesson_answer_id + answer_idx}">
            <jumpto>{answer.params.get("jumpto", 0)}</jumpto>
            <grade>0</grade>
            <score>{answer.params.get("score", 0)}</score>
            <flags>0</flags>
            <timecreated>{self.current_timestamp}</timecreated>
            <timemodified>{self.current_timestamp}</timemodified>
            <answer_text>{answer.text if answer.text!= "" else "@#wronganswer#@"}</answer_text>
            <response>$@NULL@$</response>
            <answerformat>0</answerformat>
            <responseformat>0</responseformat>
            <attempts>
            </attempts>
          </answer>
"""
                    page_content += answer_content

                MoodleActivity.next_lesson_answer_id += len(page.moodle_links)
                page_content += """        </answers>
        <branches>
        </branches>
      </page>
"""
                file_content += page_content

        MoodleActivity.next_lesson_page_id += len(self.lesson_md.pages)*10 if self.lesson_md else 0
        file_content += """    </pages>
    <grades>
    </grades>
    <timers>
    </timers>
    <overrides>
    </overrides>    
  </lesson>
</activity>
"""
        with open("lesson.xml", "w", encoding="utf-8") as f:
            f.write(file_content)



    @override
    def generate(self) -> None:
        os.makedirs(f"{self.modulename}_{self.module_id}", exist_ok=True)
        os.chdir(f"{self.modulename}_{self.module_id}")

        self._generate_empty_("grade_history.xml", "grade_history", "grade_grades")
        self._generate_empty_("grades.xml", "activity_gradebook", ["grade_items", "grade_letters"])
        self.__generate_inforef__()
        self.__generate_module__()
        if self.modulename == "resource":
            self.__generate_resource__()
        elif self.modulename == "scorm":
            self.__generate_scorm__()
        elif self.modulename == "lesson":
            self.__generate_lesson__()
        self._generate_empty_("roles.xml", "roles", ["role_overrides", "role_assignments"])

        os.chdir("..")  # leave activity directory
