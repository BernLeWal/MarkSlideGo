"""
Moodle backup representation for Moodle backup structure.
Provides methods to generate the complete Moodle backup structure including files, activities, sections, and course information
"""

import hashlib
import os
from typing import override
from markslidego.file_utils import remove_dir_recursively, remove_file_if_exists, zip_current_directory
from markslidego.generate import create_ims_manifest, generate, is_source_newer
from markslidego.moodle.base import MoodleBase
from markslidego.moodle.file import MoodleFile
from markslidego.moodle.activity import MoodleActivity
from markslidego.moodle.course import MoodleCourse
from markslidego.moodle.section import MoodleSection
from markslidego.markdown_utils import get_md_info



class MoodleBackup(MoodleBase):
    def __init__(self, course_name, course_title, course_id):
        super().__init__()
        self.course = MoodleCourse(course_name, course_title, course_id)
        self.files:list[MoodleFile] = []
        self.activities:list[MoodleActivity] = []
        self.sections:dict[str,MoodleSection] = {}
        self.filename:str = ""

        # generate a SHA1 hash from course name and id
        hash_input = f"{course_name}{course_id}".encode("utf-8")
        self.backup_hash = hashlib.sha1(hash_input).hexdigest()


    def __generate_files__(self) -> None:
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



    def __generate_groups__(self) -> None:
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


    def __generate_roles__(self) -> None:
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


    @override
    def generate(self) -> None:
        file_content =  f"""<?xml version="1.0" encoding="UTF-8"?>
<moodle_backup>
  <information>
    <name>{self.filename}</name>
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
        <value>{self.filename}</value>
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


    def create_section(self, md_file:str, topic_name:str) -> MoodleSection:
        """ Factory method to create a MoodleSection and add it to the backup """
        topic_info = get_md_info(os.path.join(os.path.dirname(md_file), "README.md"))
        topic_title = topic_name.replace("-", " ").title()
        topic_desc = ""
        if topic_info is not None and 'title' in topic_info:
            topic_title = topic_info['title']
            topic_desc = topic_info['description']

        print(f"Creating section {topic_name}: {topic_title}")
        section = MoodleSection(topic_name, topic_title, len(self.sections)+1)
        section.summary = topic_desc
        self.sections[topic_name] = section
        return section


    def create_activity(self, section:MoodleSection, activity_title:str, target_file:str, source_file:str, options):
        """ Factory method to create a MoodleActivity and add it to the backup """
        if options is not None and '--scorm' in options:
            is_scorm = True
        else:
            is_scorm = False

        if is_source_newer(source_file, target_file):
            course_title = self.course.title
            course_name = self.course.name
            print(f"Generating material: {source_file} -> {target_file}")
            if is_scorm:
                create_ims_manifest(target_file, course_name, course_title, activity_title)

            generate(source_file, target_file, options)

        if is_scorm:
            target_file = target_file.replace(".html", ".zip")

        activity_name = os.path.splitext(os.path.basename(target_file))[0]
        print(f"Creating activity {activity_name} from {target_file} scorm={is_scorm}")
        moodle_activity = MoodleActivity(activity_name, activity_title, "scorm" if is_scorm else "resource")
        if is_scorm:
            scorm_files = MoodleFile.unzip_and_add(target_file)
            moodle_activity.files.extend(scorm_files)
            self.files.extend(scorm_files)
        else:
            moodle_file = MoodleFile(target_file)
            moodle_activity.files.append(moodle_file)
            self.files.append(moodle_file)
        section.activities.append(moodle_activity)
        moodle_activity.section = section
        self.activities.append(moodle_activity)


    def generate_mbz(self, mbz_filename:str, removeIntermediateFiles:bool = False, replaceExisting:bool = True) -> None:
        os.makedirs("output", exist_ok=True)
        os.chdir("output")
        mbz_directory = mbz_filename.replace(".mbz", "")
        if replaceExisting:
            remove_dir_recursively(mbz_directory)
            remove_file_if_exists(mbz_filename)
        os.makedirs(mbz_directory, exist_ok=not replaceExisting)
        os.chdir(mbz_directory)

        self.__generate_files__()
        self.__generate_groups__()
        self._generate_empty_("outcomes.xml", "outcomes_definition")
        self._generate_empty_("questions.xml", "question_categories")
        self.__generate_roles__()
        self._generate_empty_("scales.xml", "scales_definition")

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
        self.filename = mbz_filename
        self.generate()

        zip_current_directory(".mbz")
        if removeIntermediateFiles and os.path.exists(mbz_directory):
            remove_dir_recursively(mbz_directory)
        os.chdir("..")  # leave mbz directory

        os.chdir("..")  # leave output directory
        MoodleFile.remove_intermediate_dirs()
        print(f"Generated {mbz_filename} with {len(self.sections)} sections, {len(self.activities)} activities, and {len(self.files)} files.")


    def generate_zip(self, zip_filename:str, removeIntermediateFiles:bool = False, replaceExisting:bool = True) -> None:
        os.makedirs("output", exist_ok=True)
        os.chdir("output")
        zip_directory = zip_filename.replace(".zip", "")
        if replaceExisting:
            remove_dir_recursively(zip_directory)
            remove_file_if_exists(zip_filename)
        os.makedirs(zip_directory, exist_ok=not replaceExisting)
        os.chdir(zip_directory)
        filecount = 0

        # ----- Sections -----
        if self.sections:
            for section in self.sections.values():
                if section.activities:
                    # ----- Activities -----
                    os.makedirs(section.name, exist_ok=True)
                    for activity in section.activities:
                        os.makedirs(f"{section.name}/{activity.name}", exist_ok=True)
                        for f in activity.files:
                            if f.copy_file_to(f"{section.name}/{activity.name}"):
                                filecount += 1

        zip_current_directory()
        if removeIntermediateFiles and os.path.exists(zip_directory):
            remove_dir_recursively(zip_directory)
        os.chdir("..")  # leave zip directory

        os.chdir("..")  # leave output directory
        MoodleFile.remove_intermediate_dirs()
        print(f"Generated {zip_filename} with {len(self.sections)} sections, {len(self.activities)} activities, and {filecount} files.")