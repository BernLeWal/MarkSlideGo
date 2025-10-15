import os
import pytest
from generate_moodle import MoodleBackup, MoodleFile, MoodleActivity, MoodleSection


# -------------------------- For development purposes only --------------------------
def test_empty():
    # Scenario 1: generate an empty course backup
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    generator = MoodleBackup("Empty", "Empty Course", 16200)
    generator.generate_mbz("backup-moodle2-course-empty.mbz")


def test_files():
    # Scenario 2: generate a course backup with file references
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    generator = MoodleBackup("Files", "Course with Files", 16201)
    pdf_file1 = MoodleFile("test/java-kickstart.pdf")
    generator.files.append(pdf_file1)
    pdf_file2 = MoodleFile("test/csharp-kickstart.pdf")
    generator.files.append(pdf_file2)

    pdf_activity1 = MoodleActivity("java-kickstart", "Java: Programming intro and development tools (PDF)")
    pdf_activity1.files.append(pdf_file1)
    generator.activities.append(pdf_activity1)
    pdf_activity2 = MoodleActivity("csharp-kickstart", "C#: Programming intro and development tools (PDF)")
    pdf_activity2.files.append(pdf_file2)
    generator.activities.append(pdf_activity2)


    pdf_section = MoodleSection("Class-1", "Class 1: Kickstart Programming", 6)
    pdf_section.activities.append(pdf_activity1)
    pdf_activity1.section = pdf_section
    pdf_section.activities.append(pdf_activity2)
    pdf_activity2.section = pdf_section
    generator.sections["Class 1"] = pdf_section

    generator.generate_mbz("backup-moodle2-course-2pdf.mbz")


def test_scorm():
    # Scenario 3: generate a course backup with a SCORM activity
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    generator = MoodleBackup("Scorm", "Course with SCORM", 16202)
    scorm_files = MoodleFile.unzip_and_add("test/oop-basics.zip")
    generator.files.extend(scorm_files)

    scorm_activity = MoodleActivity("oop-basics", "Basics of Object-Oriented Programming", "scorm")
    scorm_activity.files.extend(scorm_files)
    generator.activities.append(scorm_activity)

    scorm_section = MoodleSection("SS-B", "Self-Study B: Object-Oriented Programming Recap", 7)
    scorm_section.activities.append(scorm_activity)
    scorm_activity.section = scorm_section
    generator.sections["Self-Study B"] = scorm_section

    generator.generate_mbz("backup-moodle2-course-scorm.mbz")
    generator.remove_dir_recursively("test/oop-basics")


def test_all():
    # Scenario 4: generate a course backup with a SCORM activity and PDF activities
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    generator = MoodleBackup("Complete", "Course Complete", 16203)
    scorm_files = MoodleFile.unzip_and_add("test/oop-basics.zip")
    generator.files.extend(scorm_files)
    pdf_file1 = MoodleFile("test/java-kickstart.pdf")
    generator.files.append(pdf_file1)
    pdf_file2 = MoodleFile("test/csharp-kickstart.pdf")
    generator.files.append(pdf_file2)

    scorm_activity = MoodleActivity("oop-basics", "Basics of Object-Oriented Programming", "scorm")
    scorm_activity.files.extend(scorm_files)
    generator.activities.append(scorm_activity)
    pdf_activity1 = MoodleActivity("java-kickstart", "Java: Programming intro and development tools (PDF)")
    pdf_activity1.files.append(pdf_file1)
    generator.activities.append(pdf_activity1)
    pdf_activity2 = MoodleActivity("csharp-kickstart", "C#: Programming intro and development tools (PDF)")
    pdf_activity2.files.append(pdf_file2)
    generator.activities.append(pdf_activity2)

    all_section = MoodleSection("SS-B", "Self-Study B: Object-Oriented Programming Recap", 7)
    all_section.activities.append(scorm_activity)
    scorm_activity.section = all_section
    all_section.activities.append(pdf_activity1)
    pdf_activity1.section = all_section
    all_section.activities.append(pdf_activity2)
    pdf_activity2.section = all_section

    generator.sections["Self-Study B"] = all_section

    generator.generate_mbz("backup-moodle2-course-all.mbz")
    generator.remove_dir_recursively("test/oop-basics")



# --------------------------------------------
if __name__ == "__main__":
    import pytest
    pytest.main(["-q", __file__])