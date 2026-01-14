from markslidego.moodle.base import MoodleBase


import os


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