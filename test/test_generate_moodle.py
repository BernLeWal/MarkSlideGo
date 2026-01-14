import os
import shutil
import zipfile
import pytest
import sys
from pathlib import Path

# Ensure repository root is on sys.path so tests can import the package
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from markslidego.generate_moodle import MoodleBackup, MoodleFile, MoodleActivity, MoodleSection


@pytest.fixture(autouse=True)
def use_tmp_cwd(tmp_path):
    """Change working directory to a temporary path for each test and clean up."""
    old_cwd = os.getcwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(old_cwd)
    shutil.rmtree(tmp_path, ignore_errors=True)


def create_dummy_pdf(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"%PDF-1.4\n%dummy\n")


def test_empty_creates_mbz(tmp_path):
    generator = MoodleBackup("Empty", "Empty Course", 16200)
    # generate_mbz writes into ./output/<name>.mbz
    generator.generate_mbz("backup-moodle2-course-empty.mbz")
    out = tmp_path / "output" / "backup-moodle2-course-empty.mbz"
    assert out.exists()
    assert zipfile.is_zipfile(out)


def test_files_creates_mbz_with_files(tmp_path):
    # Prepare dummy files
    create_dummy_pdf(tmp_path / "test" / "java-kickstart.pdf")
    create_dummy_pdf(tmp_path / "test" / "csharp-kickstart.pdf")

    generator = MoodleBackup("Files", "Course with Files", 16201)
    pdf_file1 = MoodleFile(str(tmp_path / "test" / "java-kickstart.pdf"))
    generator.files.append(pdf_file1)
    pdf_file2 = MoodleFile(str(tmp_path / "test" / "csharp-kickstart.pdf"))
    generator.files.append(pdf_file2)

    pdf_activity1 = MoodleActivity("java-kickstart", "Java: Programming intro and development tools (PDF)")
    pdf_activity1.files.append(pdf_file1)
    generator.activities.append(pdf_activity1)
    pdf_activity2 = MoodleActivity("csharp-kickstart", "C#: Programming intro and development tools (PDF)")
    pdf_activity2.files.append(pdf_file2)
    generator.activities.append(pdf_activity2)

    pdf_section = MoodleSection("Class-1","Class 1: Kickstart Programming", 6)
    pdf_section.activities.append(pdf_activity1)
    pdf_activity1.section = pdf_section
    pdf_section.activities.append(pdf_activity2)
    pdf_activity2.section = pdf_section
    # generator.sections is a dict in the codebase
    generator.sections["Class 1"] = pdf_section

    generator.generate_mbz("backup-moodle2-course-2pdf.mbz")
    out = tmp_path / "output" / "backup-moodle2-course-2pdf.mbz"
    assert out.exists()
    assert zipfile.is_zipfile(out)


def test_scorm_creates_mbz_and_cleans_up(tmp_path):
    # Prepare a small zip that mimics a scorm package
    scorm_dir = tmp_path / "test" / "oop-basics"
    scorm_dir.mkdir(parents=True)
    (scorm_dir / "imsmanifest.xml").write_text("<manifest></manifest>")
    zip_path = tmp_path / "test" / "oop-basics.zip"
    with zipfile.ZipFile(zip_path, 'w') as z:
        z.write(scorm_dir / "imsmanifest.xml", arcname="imsmanifest.xml")

    generator = MoodleBackup("Scorm", "Course with SCORM", 16202)
    scorm_files = MoodleFile.unzip_and_add(str(zip_path))
    generator.files.extend(scorm_files)

    scorm_activity = MoodleActivity("oop-basics", "Basics of Object-Oriented Programming", "scorm")
    scorm_activity.files.extend(scorm_files)
    generator.activities.append(scorm_activity)

    scorm_section = MoodleSection("SS-B", "Self-Study B: Object-Oriented Programming Recap", 7)
    scorm_section.activities.append(scorm_activity)
    scorm_activity.section = scorm_section
    generator.sections["Self-Study B"] = scorm_section

    generator.generate_mbz("backup-moodle2-course-scorm.mbz")
    out = tmp_path / "output" / "backup-moodle2-course-scorm.mbz"
    assert out.exists()
    assert zipfile.is_zipfile(out)


def test_all_creates_full_mbz(tmp_path):
    # Prepare files
    scorm_dir = tmp_path / "test" / "oop-basics"
    scorm_dir.mkdir(parents=True)
    (scorm_dir / "imsmanifest.xml").write_text("<manifest></manifest>")
    zip_path = tmp_path / "test" / "oop-basics.zip"
    with zipfile.ZipFile(zip_path, 'w') as z:
        z.write(scorm_dir / "imsmanifest.xml", arcname="imsmanifest.xml")

    create_dummy_pdf(tmp_path / "test" / "java-kickstart.pdf")
    create_dummy_pdf(tmp_path / "test" / "csharp-kickstart.pdf")

    generator = MoodleBackup("Complete", "Course Complete", 16203)
    scorm_files = MoodleFile.unzip_and_add(str(zip_path))
    generator.files.extend(scorm_files)
    pdf_file1 = MoodleFile(str(tmp_path / "test" / "java-kickstart.pdf"))
    generator.files.append(pdf_file1)
    pdf_file2 = MoodleFile(str(tmp_path / "test" / "csharp-kickstart.pdf"))
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
    out = tmp_path / "output" / "backup-moodle2-course-all.mbz"
    assert out.exists()
    assert zipfile.is_zipfile(out)


# --------------------------------------------
if __name__ == "__main__":
    import pytest
    pytest.main(["-q", __file__])