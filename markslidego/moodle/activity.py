"""
Moodle activity representation for Moodle backup structure.
Provides methods to generate XML entries for Moodle activities in the backup.
"""
import os
from typing import override
from markslidego.moodle.base import MoodleBase
from markslidego.moodle.file import MoodleFile
from markslidego.moodle.section import MoodleSection


class MoodleActivity(MoodleBase):

    next_activity_id = 20000
    next_module_id = 25000

    def __init__(self, name:str, title:str, modulename:str="resource"):
        super().__init__()
        self.id = MoodleActivity.next_activity_id
        MoodleActivity.next_activity_id += 1
        self.module_id = MoodleActivity.next_module_id
        MoodleActivity.next_module_id += 1
        self.name = name
        self.title = title.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        self.modulename = modulename

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
        self._generate_empty_("roles.xml", "roles", ["role_overrides", "role_assignments"])

        os.chdir("..")  # leave activity directory