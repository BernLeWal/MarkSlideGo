#!/usr/bin/env python3

import os
import hashlib
import sys
import time
import zipfile
import xml.etree.ElementTree as ET

from generate import create_ims_manifest, generate, is_source_newer


class MoodleBase:
    def __init__(self):
        self.MOODLE_VERSION = "2024100705"
        self.MOODLE_RELEASE = "4.5.5 (Build: 20250609)"
        self.BACKUP_VERSION ="2024100700"
        self.BACKUP_RELEASE = "4.5"

        self.ROLE_ID = "5"
        self.USER_ID = "17726"
        
        self.current_timestamp = int(time.time())


    def generate_empty(self, filename, rootElemName, childElemName = None) -> None:
        file_content = f"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        if rootElemName:
            file_content += f"<{rootElemName}>\n"
        if childElemName:
            if isinstance(childElemName, list):
                for child in childElemName:
                    if isinstance(child, str):
                        file_content += f"  <{child}>\n"
                        file_content += f"  </{child}>\n"
            elif isinstance(childElemName, str):
                file_content += f"  <{childElemName}>\n"
                file_content += f"  </{childElemName}>\n"
        
        if rootElemName:
            file_content += f"</{rootElemName}>\n"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(file_content)


    def remove_dir_recursively(self, path:str) -> None:
        """ Remove a directory and all its contents recursively """
        if os.path.exists(path):
            for root, dirs, files in os.walk(path, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(path)


    def remove_file_if_exists(self, filepath:str) -> None:
        """ Remove a file if it exists """
        if os.path.exists(filepath):
            os.remove(filepath)



    

class MoodleFile(MoodleBase):

    next_file_id = 10000
    next_context_id = 15000

    intermediate_dirs = []

    def __init__(self, filepath:str, component:str = "mod_resource", context_id:int=0, filearea:str="content"):
        super().__init__()
        self.file_id = MoodleFile.next_file_id
        MoodleFile.next_file_id += 1
        if context_id != 0:
            self.context_id = context_id
        else:
          self.context_id = MoodleFile.next_context_id
          MoodleFile.next_context_id += 1
        self.filepath = filepath
        self.subdir = ""
        self.filearea = filearea
        self.component = component

        self.filename = os.path.basename(filepath)
        self.filesize = os.path.getsize(filepath)
        self.mimetype = self.get_mime_type(filepath)
        self.creationtime = int(os.path.getctime(filepath))
        self.modificationtime = int(os.path.getmtime(filepath))

        # self.content_hash is the SHA1 hash of the file content
        sha1 = hashlib.sha1()
        with open(filepath, "rb") as f:
            while True:
                data = f.read(65536)  # Read in 64k chunks
                if not data:
                    break
                sha1.update(data)
        self.content_hash = sha1.hexdigest()

        # if file has structured content, then store them as dictionary
        self.content_dict = {}
        if self.filename == "imsmanifest.xml":
            with open(filepath, "r", encoding="utf-8") as f:
                xml_string = f.read()
            self.content_dict = self.parse_imsmanifest(xml_string)


    def get_mime_type(self, filepath:str) -> str:
        # very basic mime type detection based on file extension
        ext = os.path.splitext(filepath)[1].lower()
        if ext == ".pdf":
            return "application/pdf"
        elif ext in [".jpg", ".jpeg"]:
            return "image/jpeg"
        elif ext == ".png":
            return "image/png"
        elif ext == ".gif":
            return "image/gif"
        elif ext == ".txt":
            return "text/plain"
        elif ext == ".html" or ext == ".htm":
            return "text/html"
        elif ext == ".md":
            return "text/markdown"
        elif ext == ".zip":
            return "application/zip"
        elif ext == ".doc":
            return "application/msword"
        elif ext == ".docx":
            return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif ext == ".ppt":
            return "application/vnd.ms-powerpoint"
        elif ext == ".pptx":
            return "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        elif ext == ".xls":
            return "application/vnd.ms-excel"
        elif ext == ".xlsx":
            return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        else:
            return "application/octet-stream"  # default binary type


    def generate(self) -> None:
        files_subdir = self.content_hash[0:2]
        os.makedirs(f"{files_subdir}", exist_ok=True)
        os.chdir(f"{files_subdir}")
        # copy file contents to self.content_hash
        with open(self.content_hash, "wb") as out_file:
            # open source file and copy contents
            with open(os.path.join("..", "..", "..", "..", self.filepath), "rb") as in_file:
                while True:
                    data = in_file.read(65536)  # Read in 64k chunks
                    if not data:
                        break
                    out_file.write(data)
        os.chdir("..")


    def parse_imsmanifest(self, xml_string:str) -> dict:
        ns = {'imscp': 'http://www.imsglobal.org/xsd/imscp_v1p1'}
        result = {}

        try:

            root = ET.fromstring(xml_string)
            # /manifest[identifier]
            result['manifest.identifier'] = root.attrib.get('identifier')

            # /manifest/organizations/organization[identifier]
            org = root.find('imscp:organizations/imscp:organization', ns)
            result['organization.identifier'] = org.attrib.get('identifier') if org is not None else None

            # /manifest/organizations/organization/title
            org_title = org.find('imscp:title', ns) if org is not None else None
            result['organization.title'] = org_title.text if org_title is not None else None

            # /manifest/organizations/organization/item[identifier]
            item = org.find('imscp:item', ns) if org is not None else None
            result['item.identifier'] = item.attrib.get('identifier') if item is not None else None

            # /manifest/organizations/organization/item/title
            item_title = item.find('imscp:title', ns) if item is not None else None
            result['item.title'] = item_title.text if item_title is not None else None

            # /manifest/resources/resource[href]
            resource = root.find('imscp:resources/imscp:resource', ns)
            result['resource.href'] = resource.attrib.get('href') if resource is not None else None

        except ET.ParseError as e:
            print(f"Error parsing imsmanifest.xml: {e}", file=sys.stderr)
            print(xml_string, file=sys.stderr)

        return result


    @staticmethod
    def unzip_and_add(zip_filepath:str, component:str="mod_scorm") -> list:
        zip_contents_dir = zip_filepath.replace(".zip", "_unzipped")
        with zipfile.ZipFile(zip_filepath, 'r') as zip_ref:
            zip_ref.extractall(zip_contents_dir)
        MoodleFile.intermediate_dirs.append(zip_contents_dir)

        context_id = MoodleFile.next_context_id
        MoodleFile.next_context_id += 1
        result = []
        # walk through the files in the extracted directory recursivly and create MoodleFile instances
        for root, dirs, files in os.walk(zip_contents_dir):
            for name in files:
                filepath = os.path.join(root, name)
                moodlefile = MoodleFile(filepath, component, context_id)
                if zip_contents_dir != root:
                    moodlefile.subdir = root.replace(zip_contents_dir, "")
                result.append(moodlefile)
        result.append(MoodleFile(zip_filepath, component, context_id))
        return result


    @staticmethod
    def remove_intermediate_dirs():
        for intermediate_dir in MoodleFile.intermediate_dirs:
            if os.path.exists(intermediate_dir):
                for root, dirs, files in os.walk(intermediate_dir, topdown=False):
                    for name in files:
                        os.remove(os.path.join(root, name))
                    for name in dirs:
                        os.rmdir(os.path.join(root, name))
                os.rmdir(intermediate_dir)


class MoodleActivity(MoodleBase):

    next_activity_id = 20000
    next_module_id = 25000

    def __init__(self, title:str, modulename:str="resource"):
        super().__init__()
        self.id = MoodleActivity.next_activity_id
        MoodleActivity.next_activity_id += 1
        self.module_id = MoodleActivity.next_module_id
        MoodleActivity.next_module_id += 1
        self.title = title.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        self.modulename = modulename

        self.files:list[MoodleFile] = []
        self.section:MoodleSection|None = None


    def generate_inforef(self) -> None:
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


    def generate_module(self) -> None:
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


    def generate_resource(self) -> None:
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


    def generate_scorm(self) -> None:
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


    def generate(self) -> None:
        os.makedirs(f"{self.modulename}_{self.module_id}", exist_ok=True)
        os.chdir(f"{self.modulename}_{self.module_id}")

        self.generate_empty("grade_history.xml", "grade_history", "grade_grades")
        self.generate_empty("grades.xml", "activity_gradebook", ["grade_items", "grade_letters"])
        self.generate_inforef()
        self.generate_module()
        if self.modulename == "resource":
            self.generate_resource()
        elif self.modulename == "scorm":
            self.generate_scorm()
        self.generate_empty("roles.xml", "roles", ["role_overrides", "role_assignments"])

        os.chdir("..")  # leave activity directory




class MoodleSection(MoodleBase):

    next_section_id = 30000

    def __init__(self, title:str, number:int):
        super().__init__()
        self.id = MoodleSection.next_section_id
        MoodleSection.next_section_id += 1
        self.title = title.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        self.number = number
        self.summary = ""

        self.activities:list[MoodleActivity] = [] 


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




class MoodleCourse(MoodleBase):
    def __init__(self, name, title, course_id):
        super().__init__()
        self.name = name
        self.title = title.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        self.id = course_id


    def generate_course(self) -> None:
        file_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<course id="{self.id}" contextid="946563">
  <shortname>{self.name}</shortname>
  <fullname>{self.title}</fullname>
  <idnumber></idnumber>
  <summary></summary>
  <summaryformat>1</summaryformat>
  <format>scfhtw</format>
  <showgrades>1</showgrades>
  <newsitems>5</newsitems>
  <startdate>1614121200</startdate>
  <enddate>0</enddate>
  <marker>-1</marker>
  <maxbytes>20971520</maxbytes>
  <legacyfiles>0</legacyfiles>
  <showreports>0</showreports>
  <visible>1</visible>
  <groupmode>0</groupmode>
  <groupmodeforce>0</groupmodeforce>
  <defaultgroupingid>0</defaultgroupingid>
  <lang>en</lang>
  <theme></theme>
  <timecreated>1614080028</timecreated>
  <timemodified>1756978865</timemodified>
  <requested>0</requested>
  <showactivitydates>0</showactivitydates>
  <showcompletionconditions>$@NULL@$</showcompletionconditions>
  <pdfexportfont>$@NULL@$</pdfexportfont>
  <enablecompletion>0</enablecompletion>
  <completionnotify>0</completionnotify>
  <category id="2711">
    <name>Software Engineering &amp; Architecture</name>
    <description></description>
  </category>
  <tags>
  </tags>
  <customfields>
  </customfields>
  <courseformatoptions>
    <courseformatoption>
      <format>scfhtw</format>
      <sectionid>0</sectionid>
      <name>advancedoptions</name>
      <value>Alle weiteren Parameter sollten für standardisierte Lehrverantstaltungen nicht geändert werden!</value>
    </courseformatoption>
    <courseformatoption>
      <format>scfhtw</format>
      <sectionid>0</sectionid>
      <name>coursedisplay</name>
      <value>Course layout</value>
    </courseformatoption>
    <courseformatoption>
      <format>scfhtw</format>
      <sectionid>0</sectionid>
      <name>customsectionlisttitle</name>
      <value></value>
    </courseformatoption>
    <courseformatoption>
      <format>scfhtw</format>
      <sectionid>0</sectionid>
      <name>customteacherlisttitle</name>
      <value></value>
    </courseformatoption>
    <courseformatoption>
      <format>scfhtw</format>
      <sectionid>0</sectionid>
      <name>grading</name>
      <value>&lt;h3&gt;Assessment&lt;/h3&gt;...</value>
    </courseformatoption>
    <courseformatoption>
      <format>scfhtw</format>
      <sectionid>0</sectionid>
      <name>gradingcriteria</name>
      <value>&lt;h3&gt;Assessment Criteria&lt;/h3&gt;...</value>
    </courseformatoption>
    <courseformatoption>
      <format>scfhtw</format>
      <sectionid>0</sectionid>
      <name>hiddensections</name>
      <value>1</value>
    </courseformatoption>
    <courseformatoption>
      <format>scfhtw</format>
      <sectionid>0</sectionid>
      <name>maxteacherlistlength</name>
      <value>2</value>
    </courseformatoption>
    <courseformatoption>
      <format>scfhtw</format>
      <sectionid>0</sectionid>
      <name>scfhtwexpandsections</name>
      <value>0</value>
    </courseformatoption>
    <courseformatoption>
      <format>scfhtw</format>
      <sectionid>0</sectionid>
      <name>schedule</name>
      <value>$@NULL@$</value>
    </courseformatoption>
    <courseformatoption>
      <format>scfhtw</format>
      <sectionid>0</sectionid>
      <name>showheader</name>
      <value>1</value>
    </courseformatoption>
    <courseformatoption>
      <format>scfhtw</format>
      <sectionid>0</sectionid>
      <name>showimage</name>
      <value>0</value>
    </courseformatoption>
    <courseformatoption>
      <format>scfhtw</format>
      <sectionid>0</sectionid>
      <name>showinfo</name>
      <value>1</value>
    </courseformatoption>
    <courseformatoption>
      <format>scfhtw</format>
      <sectionid>0</sectionid>
      <name>showoverview</name>
      <value>1</value>
    </courseformatoption>
    <courseformatoption>
      <format>scfhtw</format>
      <sectionid>0</sectionid>
      <name>showteachers</name>
      <value>1</value>
    </courseformatoption>
  </courseformatoptions>
</course>
"""
        with open("course.xml", "w", encoding="utf-8") as f:
            f.write(file_content)


    def generate_enrolments(self) -> None:
        file_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<enrolments>
  <enrols>
    <enrol id="30241">
      <enrol>manual</enrol>
      <status>0</status>
      <name>$@NULL@$</name>
      <enrolperiod>0</enrolperiod>
      <enrolstartdate>0</enrolstartdate>
      <enrolenddate>0</enrolenddate>
      <expirynotify>0</expirynotify>
      <expirythreshold>86400</expirythreshold>
      <notifyall>0</notifyall>
      <password>$@NULL@$</password>
      <cost>$@NULL@$</cost>
      <currency>$@NULL@$</currency>
      <roleid>{self.ROLE_ID}</roleid>
      <customint1>$@NULL@$</customint1>
      <customint2>$@NULL@$</customint2>
      <customint3>$@NULL@$</customint3>
      <customint4>$@NULL@$</customint4>
      <customint5>$@NULL@$</customint5>
      <customint6>$@NULL@$</customint6>
      <customint7>$@NULL@$</customint7>
      <customint8>$@NULL@$</customint8>
      <customchar1>$@NULL@$</customchar1>
      <customchar2>$@NULL@$</customchar2>
      <customchar3>$@NULL@$</customchar3>
      <customdec1>$@NULL@$</customdec1>
      <customdec2>$@NULL@$</customdec2>
      <customtext1>$@NULL@$</customtext1>
      <customtext2>$@NULL@$</customtext2>
      <customtext3>$@NULL@$</customtext3>
      <customtext4>$@NULL@$</customtext4>
      <timecreated>1614080028</timecreated>
      <timemodified>1614080028</timemodified>
      <user_enrolments>
      </user_enrolments>
    </enrol>
  </enrols>
</enrolments>
"""
        with open("enrolments.xml", "w", encoding="utf-8") as f:
            f.write(file_content)


    def generate_inforef(self) -> None:
        file_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<inforef>
  <roleref>
    <role>
      <id>{self.ROLE_ID}</id>
    </role>
  </roleref>
</inforef>
"""
        with open("inforef.xml", "w", encoding="utf-8") as f:
            f.write(file_content)


    def generate(self) -> None:
        os.makedirs("course", exist_ok=True)
        os.chdir("course")

        self.generate_empty("completiondefaults.xml", "course_completion_defaults")
        self.generate_course()
        self.generate_enrolments()
        self.generate_inforef()
        self.generate_empty("roles.xml", "roles", ["role_overrides", "role_assignments"])

        os.chdir("..")  # leave course directory




class MoodleBackup(MoodleBase):
    def __init__(self, course_name, course_title, course_id):
        super().__init__()
        self.course = MoodleCourse(course_name, course_title, course_id)
        self.files:list[MoodleFile] = []
        self.activities:list[MoodleActivity] = []
        self.sections:dict[str,MoodleSection] = {}

        # generate a SHA1 hash from course name and id
        hash_input = f"{course_name}{course_id}".encode("utf-8")
        self.backup_hash = hashlib.sha1(hash_input).hexdigest()


    def zip_current_directory_to_mbz(self) -> None:
        mbz_filename = os.path.basename(os.getcwd()) + ".mbz"
        zip_path = os.path.join("..", mbz_filename)
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk("."):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, ".")
                    zipf.write(file_path, arcname)


    def generate_files(self) -> None:
        file_content = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        file_content += "<files>\n"
        for f in self.files:
            file_content += f"""  <file id="{f.file_id}">
    <contenthash>{f.content_hash}</contenthash>
    <contextid>{f.context_id}</contextid>
    <component>{f.component}</component>
    <filearea>{f.filearea}</filearea>
    <itemid>0</itemid>
    <filepath>{f.subdir}/</filepath>
    <filename>{f.filename}</filename>
    <userid>$@NULL@$</userid>
    <filesize>{f.filesize}</filesize>
    <mimetype>{f.mimetype}</mimetype>
    <status>0</status>
    <timecreated>{f.creationtime}</timecreated>
    <timemodified>{f.modificationtime}</timemodified>
    <source>{f.filename if f.component=='mod_resource' else '$@NULL@$'}</source>
    <author>$@NULL@$</author>
    <license>$@NULL@$</license>
    <sortorder>1</sortorder>
    <repositorytype>$@NULL@$</repositorytype>
    <repositoryid>$@NULL@$</repositoryid>
    <reference>$@NULL@$</reference>
  </file>
"""
        file_content += "</files>\n"
        with open("files.xml", "w", encoding="utf-8") as f:
            f.write(file_content)



    def generate_groups(self) -> None:
        file_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<groups>
  <groupcustomfields>
  </groupcustomfields>
  <groupings>
    <groupingcustomfields>
    </groupingcustomfields>
  </groupings>
</groups>
"""
        with open("groups.xml", "w", encoding="utf-8") as f:
            f.write(file_content)


    def generate_roles(self) -> None:
        file_content = """<?xml version="1.0" encoding="UTF-8"?>
<roles_definition>
  <role id=\"""" + self.ROLE_ID + """\">
    <name>{mlang de}TeilnehmerIn{mlang}{mlang en}Participant{mlang}</name>
    <shortname>student</shortname>
    <nameincourse>$@NULL@$</nameincourse>
    <description>Standardrolle - für Studierende in Lehrveranstaltungen und für normale TeilnehmerInnen in nicht-LV Kursen</description>
    <sortorder>13</sortorder>
    <archetype>student</archetype>
  </role>
</roles_definition>
"""
        with open("roles.xml", "w", encoding="utf-8") as f:
            f.write(file_content)


    def generate_moodle_backup(self, mbz_filename:str) -> None:
        file_content =  f"""<?xml version="1.0" encoding="UTF-8"?>
<moodle_backup>
  <information>
    <name>{mbz_filename}</name>
    <moodle_version>{self.MOODLE_VERSION}</moodle_version>
    <moodle_release>{self.MOODLE_RELEASE}</moodle_release>
    <backup_version>{self.BACKUP_VERSION}</backup_version>
    <backup_release>{self.BACKUP_RELEASE}</backup_release>
    <backup_date>{self.current_timestamp}</backup_date>
    <mnet_remoteusers>0</mnet_remoteusers>
    <include_files>{len(self.files)}</include_files>
    <include_file_references_to_external_content>0</include_file_references_to_external_content>
    <original_wwwroot>https://moodle.technikum-wien.at</original_wwwroot>
    <original_site_identifier_hash>6118578f64415b7ca246939bfb24e84a</original_site_identifier_hash>
    <original_course_id>{self.course.id}</original_course_id>
    <original_course_format>scfhtw</original_course_format>
    <original_course_fullname>{self.course.title}</original_course_fullname>
    <original_course_shortname>{self.course.name}</original_course_shortname>
    <original_course_startdate>0</original_course_startdate>
    <original_course_enddate>0</original_course_enddate>
    <original_course_contextid>946563</original_course_contextid>
    <original_system_contextid>1</original_system_contextid>
    <details>
      <detail backup_id="{self.backup_hash}">
        <type>course</type>
        <format>moodle2</format>
        <interactive>1</interactive>
        <mode>70</mode>
        <execution>2</execution>
        <executiontime>0</executiontime>
      </detail>
    </details>
    <contents>
"""
        if self.activities:
            file_content += "      <activities>\n"
            for activity in self.activities:
                file_content += f"""        <activity>
          <moduleid>{activity.module_id}</moduleid>
          <sectionid>{activity.section.id if activity.section else 0}</sectionid>
          <modulename>{activity.modulename}</modulename>
          <title>{activity.title}</title>
          <directory>activities/{activity.modulename}_{activity.module_id}</directory>
          <insubsection></insubsection>
        </activity>
"""
            file_content += "      </activities>\n"

        if self.sections:
            file_content += "      <sections>\n"
            for section in self.sections.values():
                file_content += f"""        <section>
          <sectionid>{section.id}</sectionid>
          <title>{section.title}</title>
          <directory>sections/section_{section.id}</directory>
          <parentcmid></parentcmid>
          <modname></modname>
        </section>
"""
            file_content += "      </sections>\n"

        file_content += f"""      <course>
        <courseid>{self.course.id}</courseid>
        <title>{self.course.name}</title>
        <directory>course</directory>
      </course>
    </contents>
    <settings>
      <setting>
        <level>root</level>
        <name>filename</name>
        <value>{mbz_filename}</value>
      </setting>
      <setting>
        <level>root</level>
        <name>users</name>
        <value>0</value>
      </setting>
      <setting>
        <level>root</level>
        <name>anonymize</name>
        <value>0</value>
      </setting>
      <setting>
        <level>root</level>
        <name>role_assignments</name>
        <value>0</value>
      </setting>
      <setting>
        <level>root</level>
        <name>activities</name>
        <value>{len(self.activities)}</value>
      </setting>
      <setting>
        <level>root</level>
        <name>blocks</name>
        <value>0</value>
      </setting>
      <setting>
        <level>root</level>
        <name>files</name>
        <value>{len(self.files)}</value>
      </setting>
      <setting>
        <level>root</level>
        <name>filters</name>
        <value>0</value>
      </setting>
      <setting>
        <level>root</level>
        <name>comments</name>
        <value>0</value>
      </setting>
      <setting>
        <level>root</level>
        <name>badges</name>
        <value>0</value>
      </setting>
      <setting>
        <level>root</level>
        <name>calendarevents</name>
        <value>0</value>
      </setting>
      <setting>
        <level>root</level>
        <name>userscompletion</name>
        <value>0</value>
      </setting>
      <setting>
        <level>root</level>
        <name>logs</name>
        <value>0</value>
      </setting>
      <setting>
        <level>root</level>
        <name>grade_histories</name>
        <value>0</value>
      </setting>
      <setting>
        <level>root</level>
        <name>questionbank</name>
        <value>0</value>
      </setting>
      <setting>
        <level>root</level>
        <name>groups</name>
        <value>0</value>
      </setting>
      <setting>
        <level>root</level>
        <name>competencies</name>
        <value>0</value>
      </setting>
      <setting>
        <level>root</level>
        <name>customfield</name>
        <value>0</value>
      </setting>
      <setting>
        <level>root</level>
        <name>contentbankcontent</name>
        <value>0</value>
      </setting>
      <setting>
        <level>root</level>
        <name>xapistate</name>
        <value>0</value>
      </setting>
      <setting>
        <level>root</level>
        <name>legacyfiles</name>
        <value>0</value>
      </setting>
"""
        if self.sections:
            for section in self.sections.values():
                file_content += f"""      <setting>
        <level>section</level>
        <section>section_{section.id}</section>
        <name>section_{section.id}_included</name>
        <value>1</value>
      </setting>
      <setting>
        <level>section</level>
        <section>section_{section.id}</section>
        <name>section_{section.id}_userinfo</name>
        <value>0</value>
      </setting>
"""
        if self.activities:
            for activity in self.activities:
                file_content += f"""      <setting>
        <level>activity</level>
        <activity>{activity.modulename}_{activity.module_id}</activity>
        <name>{activity.modulename}_{activity.module_id}_included</name>
        <value>1</value>
      </setting>
      <setting>
        <level>activity</level>
        <activity>{activity.modulename}_{activity.module_id}</activity>
        <name>{activity.modulename}_{activity.module_id}_userinfo</name>
        <value>0</value>
      </setting>
"""
        file_content += """    </settings>
  </information>
</moodle_backup>"""

        with open("moodle_backup.xml", "w", encoding="utf-8") as f:
            f.write(file_content)


    def generate_mbz(self, mbz_filename:str, removeIntermediateFiles:bool = False, replaceExisting:bool = True) -> None:
        os.makedirs("output", exist_ok=True)
        os.chdir("output")
        mbz_directory = mbz_filename.replace(".mbz", "")
        if replaceExisting: 
            self.remove_dir_recursively(mbz_directory)
            self.remove_file_if_exists(mbz_filename)
        os.makedirs(mbz_directory, exist_ok=not replaceExisting)
        os.chdir(mbz_directory)

        self.generate_files()
        self.generate_groups()
        self.generate_empty("outcomes.xml", "outcomes_definition")
        self.generate_empty("questions.xml", "question_categories")
        self.generate_roles()
        self.generate_empty("scales.xml", "scales_definition")

        # ----- /activities -----
        if self.activities:
            os.makedirs("activities", exist_ok=True)
            os.chdir("activities")
            for activity in self.activities:
                activity.generate()
            os.chdir("..")  # leave activities directory

        # ----- /course -----
        self.course.generate()

        # ----- /files -----
        if self.files:
            os.makedirs("files", exist_ok=True)
            os.chdir("files")
            for f in self.files:
                f.generate()
            os.chdir("..")  # leave files directory

        # ----- /sections -----
        if self.sections:
            os.makedirs("sections", exist_ok=True)
            os.chdir("sections")
            for section in self.sections.values():
                section.generate()
            os.chdir("..")

        # -------------------
        self.generate_moodle_backup(mbz_filename)

        self.zip_current_directory_to_mbz()
        if removeIntermediateFiles and os.path.exists(mbz_directory):
            self.remove_dir_recursively(mbz_directory)
        os.chdir("..")  # leave mbz directory

        os.chdir("..")  # leave output directory
        MoodleFile.remove_intermediate_dirs()
        print(f"Generated {mbz_filename} with {len(self.sections)} sections, {len(self.activities)} activities, and {len(self.files)} files.")


# ------------------- Course Generation Function -------------------
def generate_section(generator:MoodleBackup, md_file:str, topic_name:str) -> MoodleSection:
    topic_info = get_md_info(os.path.join(os.path.dirname(md_file), "README.md"))
    topic_title = topic_name.replace("-", " ").title()
    topic_desc = ""
    if topic_info is not None and 'title' in topic_info:
        topic_title = topic_info['title']
        topic_desc = topic_info['description']

    print(f"Generating section {topic_name}: {topic_title}")
    section = MoodleSection(topic_title, len(generator.sections)+1)
    section.summary = topic_desc
    generator.sections[topic_name] = section    
    return section


def generate_activity(generator:MoodleBackup, section:MoodleSection, activity_title:str, target_file:str, source_file:str, options):
    if options is not None and '--scorm' in options:
        is_scorm = True
    else:
        is_scorm = False
    
    if is_source_newer(source_file, target_file):
        course_title = generator.course.title
        course_name = generator.course.name
        print(f"Generating material: {source_file} -> {target_file}")
        if is_scorm:
            create_ims_manifest(target_file, course_name, course_title, activity_title)

        generate(source_file, target_file, options)

    if is_scorm:
        target_file = target_file.replace(".html", ".zip")

    print(f"Generating activity {target_file} scorm={is_scorm}")
    moodle_activity = MoodleActivity(activity_title, "scorm" if is_scorm else "resource")
    if is_scorm:
        scorm_files = MoodleFile.unzip_and_add(target_file)
        moodle_activity.files.extend(scorm_files)
        generator.files.extend(scorm_files)
    else: 
        moodle_file = MoodleFile(target_file)
        moodle_activity.files.append(moodle_file)
        generator.files.append(moodle_file)
    section.activities.append(moodle_activity)
    moodle_activity.section = section
    generator.activities.append(moodle_activity)



def get_md_info(md_file:str) -> dict|None:
    info = {}
    if os.path.exists(md_file):
        try:
            first_line = ""
            with open(md_file, 'r', encoding='utf-8') as f:
                while line := f.readline():
                    line = line.strip()
                    if first_line == "" and line:
                        first_line = line.lstrip("# ").strip()
                        info['title'] = first_line
                        info['description'] = ""
                    elif line.startswith("# "):
                        return info # next section, stop processing
                    else: # add to description
                        info['description'] = info['description'] + line.strip() + "\n"
        except Exception:
            pass
    return info



def get_marp_info(md_file:str) -> dict|None:
  """Read the top of a markdown file and parse a Marp front-matter block.

  Reads up to 20 lines or until the second '---' marker. If a line
  'marp: true' is present in the block, returns a dict of parsed
  key: value pairs. Otherwise returns None.
  """
  if not os.path.exists(md_file):
    return None

  frontmatter = []
  inside = False
  max_lines = 20
  try:
    with open(md_file, 'r', encoding='utf-8') as f:
      for i in range(max_lines):
        line = f.readline()
        if line == '':
          break
        stripped = line.strip()
        if stripped == '---':
          if not inside:
            inside = True
            continue
          else:
            # end of frontmatter
            break
        if inside:
          frontmatter.append(stripped)
  except Exception:
    return None

  if not frontmatter:
    return None

  # parse lines as key: value
  result = {}
  found_marp_true = False
  for ln in frontmatter:
    if not ln or ln.startswith('#'):
      continue
    if ':' not in ln:
      # skip invalid lines
      continue
    key, val = ln.split(':', 1)
    key = key.strip()
    val = val.strip()
    # remove surrounding quotes if present
    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
      val = val[1:-1]
    # convert booleans
    if val.lower() == 'true':
      parsed_val = True
    elif val.lower() == 'false':
      parsed_val = False
    else:
      parsed_val = val
    result[key] = parsed_val
    if key == 'marp' and parsed_val is True:
      found_marp_true = True

  if not found_marp_true:
    return None

  return result


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
                    section = generate_section(generator, md_file, topic_name)

                activity_title = marp_info['title'] if 'title' in marp_info else os.path.basename(md_file).replace(".md", "").replace("-", " ").title()
                generate_activity(generator, section, activity_title, md_file.replace(".md", ".html"), md_file, "--scorm")
                generate_activity(generator, section, activity_title + " (PDF)", md_file.replace(".md", ".pdf"), md_file, None)



    # Generate the moodle backup .mbz file
    generator.generate_mbz(course_name + ".mbz", removeIntermediateFiles=False, replaceExisting=True)
