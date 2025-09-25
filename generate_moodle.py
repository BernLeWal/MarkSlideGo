#!/usr/bin/env python3

import os
import hashlib
import time


class MoodleGenerator:
    def __init__(self, course_name, course_id):
        self.course_name = course_name
        self.course_shortname = course_name.replace(" ", "-").upper()
        self.course_id = course_id
        self.current_timestamp = int(time.time())

        self.MOODLE_VERSION = "2024100705"
        self.MOODLE_RELEASE = "4.5.5 (Build: 20250609)"
        self.BACKUP_VERSION ="2024100700"
        self.BACKUP_RELEASE = "4.5"
        self.ROLE_ID = "5"

        # generate a SHA1 hash from course name and id
        hash_input = f"{course_name}{course_id}".encode("utf-8")
        self.backup_hash = hashlib.sha1(hash_input).hexdigest()


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


    def generate_empty(self, filename, rootElemName) -> None:
        file_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<{rootElemName}>
</{rootElemName}>
"""
        with open(filename, "w", encoding="utf-8") as f:
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


    def generate_course_course(self) -> None:
        file_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<course id="{self.course_id}" contextid="946563">
  <shortname>{self.course_shortname}</shortname>
  <fullname>{self.course_name}</fullname>
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


    def generate_course_enrolments(self) -> None:
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


    def generate_course_inforef(self) -> None:
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


    def generate_course_roles(self) -> None:
        file_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<roles>
  <role_overrides>
  </role_overrides>
  <role_assignments>
  </role_assignments>
</roles>
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
    <include_files>0</include_files>
    <include_file_references_to_external_content>0</include_file_references_to_external_content>
    <original_wwwroot>https://moodle.technikum-wien.at</original_wwwroot>
    <original_site_identifier_hash>6118578f64415b7ca246939bfb24e84a</original_site_identifier_hash>
    <original_course_id>{self.course_id}</original_course_id>
    <original_course_format>scfhtw</original_course_format>
    <original_course_fullname>{self.course_name}</original_course_fullname>
    <original_course_shortname>{self.course_shortname}</original_course_shortname>
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
      <course>
        <courseid>{self.course_id}</courseid>
        <title>{self.course_shortname}</title>
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
        <value>0</value>
      </setting>
      <setting>
        <level>root</level>
        <name>blocks</name>
        <value>0</value>
      </setting>
      <setting>
        <level>root</level>
        <name>files</name>
        <value>0</value>
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
    </settings>
  </information>
</moodle_backup>
"""
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

        # TODO: files.xml
        self.generate_empty("files.xml", "files")
        self.generate_groups()
        self.generate_empty("outcomes.xml", "outcomes_definition")
        self.generate_empty("questions.xml", "question_categories")
        self.generate_roles()
        self.generate_empty("scales.xml", "scales_definition")

        os.makedirs("course", exist_ok=True)
        os.chdir("course")

        self.generate_empty("completiondefaults.xml", "course_completion_defaults")
        self.generate_course_course()
        self.generate_course_enrolments()
        self.generate_course_inforef()
        self.generate_course_roles()

        os.chdir("..")
        self.generate_moodle_backup(mbz_filename)

        os.system(f"zip -r ../{mbz_filename} *")
        if removeIntermediateFiles and os.path.exists(mbz_directory):
            self.remove_dir_recursively(mbz_directory)




if __name__ == "__main__":
    generator = MoodleGenerator("Sample Course", 101)
    backup_xml = generator.generate_mbz("backup-moodle2-course-noname.mbz")
    print(backup_xml)