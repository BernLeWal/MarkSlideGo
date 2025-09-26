#!/usr/bin/env python3

import os
import hashlib
import time
import zipfile


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

    def __init__(self, filepath:str):
        super().__init__()
        self.file_id = MoodleFile.next_file_id
        MoodleFile.next_file_id += 1
        self.context_id = MoodleFile.next_context_id
        MoodleFile.next_context_id += 1
        self.filepath = filepath

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





class MoodleActivity(MoodleBase):

    next_activity_id = 20000
    next_module_id = 25000

    def __init__(self, title:str):
        super().__init__()
        self.id = MoodleActivity.next_activity_id
        MoodleActivity.next_activity_id += 1
        self.module_id = MoodleActivity.next_module_id
        MoodleActivity.next_module_id += 1
        self.title = title

        self.files:list[MoodleFile] = []
        self.section:MoodleSection = None


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
  <modulename>resource</modulename>
  <sectionid>{self.section.id}</sectionid>
  <sectionnumber>{self.section.number}</sectionnumber>
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


    def generate(self) -> None:
        os.makedirs(f"resource_{self.module_id}", exist_ok=True)
        os.chdir(f"resource_{self.module_id}")

        self.generate_empty("grade_history.xml", "grade_history", "grade_grades")
        self.generate_empty("grades.xml", "activity_gradebook", ["grade_items", "grade_letters"])
        self.generate_inforef()
        self.generate_module()
        self.generate_resource()
        self.generate_empty("roles.xml", "roles", ["role_overrides", "role_assignments"])

        os.chdir("..")  # leave resource_* directory


class MoodleSection(MoodleBase):

    next_section_id = 30000

    def __init__(self, title:str, number:int):
        super().__init__()
        self.id = MoodleSection.next_section_id
        MoodleSection.next_section_id += 1
        self.title = title
        self.number = number

        self.activities:list[MoodleActivity] = [] 


    def generate_section(self) -> None:
        file_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<section id="{self.id}">
  <number>{self.number}</number>
  <name>{self.title}</name>
  <summary>{self.title}</summary>
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
    def __init__(self, course_name, course_id):
        super().__init__()
        self.name = course_name
        self.shortname = course_name.replace(" ", "-").upper()
        self.id = course_id


    def generate_course(self) -> None:
        file_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<course id="{self.id}" contextid="946563">
  <shortname>{self.shortname}</shortname>
  <fullname>{self.name}</fullname>
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
    def __init__(self, course_name, course_id):
        super().__init__()
        self.course = MoodleCourse(course_name, course_id)
        self.files:list[MoodleFile] = []
        self.activities:list[MoodleActivity] = []
        self.sections:list[MoodleSection] = []

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
    <component>mod_resource</component>
    <filearea>content</filearea>
    <itemid>0</itemid>
    <filepath>/</filepath>
    <filename>{f.filename}</filename>
    <userid>{self.USER_ID}</userid>
    <filesize>{f.filesize}</filesize>
    <mimetype>{f.mimetype}</mimetype>
    <status>0</status>
    <timecreated>{f.creationtime}</timecreated>
    <timemodified>{f.modificationtime}</timemodified>
    <source>{f.filename}</source>
    <author>$@NULL@$</author>
    <license>allrightsreserved</license>
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
    <original_course_fullname>{self.course.name}</original_course_fullname>
    <original_course_shortname>{self.course.shortname}</original_course_shortname>
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
          <sectionid>{activity.section.id}</sectionid>
          <modulename>resource</modulename>
          <title>{activity.title}</title>
          <directory>activities/resource_{activity.module_id}</directory>
          <insubsection></insubsection>
        </activity>
"""
            file_content += "      </activities>\n"

        if self.sections:
            file_content += "      <sections>\n"
            for section in self.sections:
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
        <title>{self.course.shortname}</title>
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
            for section in self.sections:
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
        <activity>resource_{activity.module_id}</activity>
        <name>resource_{activity.module_id}_included</name>
        <value>1</value>
      </setting>
      <setting>
        <level>activity</level>
        <activity>resource_{activity.module_id}</activity>
        <name>resource_{activity.module_id}_userinfo</name>
        <value>0</value>
      </setting>
"""
        file_content += """    </settings>
  </information>
</moodle_backup>"""

        with open("moodle_backup.xml", "w", encoding="utf-8") as f:
            f.write(file_content)


    def generate_mbz(self, mbz_filename:str, removeIntermediateFiles:bool = False, replaceExisting:bool = True) -> None:
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
            for section in self.sections:
                section.generate()
            os.chdir("..")

        # -------------------
        self.generate_moodle_backup(mbz_filename)

        self.zip_current_directory_to_mbz()
        if removeIntermediateFiles and os.path.exists(mbz_directory):
            self.remove_dir_recursively(mbz_directory)
        os.chdir("..")  # leave mbz directory

        os.chdir("..")  # leave output directory
        print(f"Generated {mbz_filename} successfully.")


# ------------------- Test Scenarios -------------------
def test_empty():
    # Scenario 1: generate an empty course backup
    generator = MoodleBackup("Empty Course", 16200)
    generator.generate_mbz("backup-moodle2-course-empty.mbz")


def test_files():
    # Scenario 2: generate a course backup with file references
    generator = MoodleBackup("Sample Course", 16200)
    pdf_file1 = MoodleFile("test/java-kickstart.pdf")
    generator.files.append(pdf_file1)
    pdf_file2 = MoodleFile("test/csharp-kickstart.pdf")
    generator.files.append(pdf_file2)

    pdf_activity1 = MoodleActivity("Java: Programming intro and development tools (PDF)")
    pdf_activity1.files.append(pdf_file1)
    generator.activities.append(pdf_activity1)
    pdf_activity2 = MoodleActivity("C#: Programming intro and development tools (PDF)")
    pdf_activity2.files.append(pdf_file2)
    generator.activities.append(pdf_activity2)


    pdf_section = MoodleSection("Class 1: Kickstart Programming", 6)
    pdf_section.activities.append(pdf_activity1)
    pdf_activity1.section = pdf_section
    pdf_section.activities.append(pdf_activity2)
    pdf_activity2.section = pdf_section
    generator.sections.append(pdf_section)

    generator.generate_mbz("backup-moodle2-course-2pdf.mbz")

# ------------------- Main Program -------------------
if __name__ == "__main__":
    #test_empty()
    test_files()