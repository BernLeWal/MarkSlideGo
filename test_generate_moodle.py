import os
import shutil
import pytest
from generate_moodle import MoodleBackup, MoodleFile, MoodleActivity, MoodleSection

@pytest.fixture(autouse=True)
def setup_and_teardown_tmp_files(tmp_path):
    # Create dummy PDF files for testing
    pdf1 = tmp_path / "java.kickstart.pdf"
    pdf2 = tmp_path / "csharp-kickstart.pdf"
    pdf1.write_bytes(b"Java PDF content")
    pdf2.write_bytes(b"CSharp PDF content")
    # Create output directory
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    # Change working directory to tmp_path for the test
    old_cwd = os.getcwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(old_cwd)
    # Cleanup
    shutil.rmtree(tmp_path, ignore_errors=True)

def test_generate_empty_course(tmp_path):
    generator = MoodleBackup("Sample Course", 16200)
    output_file = tmp_path / "output" / "backup-moodle2-course-empty.mbz"
    generator.generate_mbz(str(output_file))
    # Check that the mbz file was created
    assert output_file.exists()
    # Optionally, check that the file is a zip archive
    import zipfile
    assert zipfile.is_zipfile(output_file)

def test_generate_course_with_files(tmp_path):
    generator = MoodleBackup("Sample Course", 16200)
    pdf_file1 = MoodleFile(str(tmp_path / "java.kickstart.pdf"))
    generator.files.append(pdf_file1)
    pdf_file2 = MoodleFile(str(tmp_path / "csharp-kickstart.pdf"))
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

    output_file = tmp_path / "output" / "backup-moodle2-course-2pdf.mbz"
    generator.generate_mbz(str(output_file))
    # Check that the mbz file was created
    assert output_file.exists()
    # Optionally, check that the file is a zip archive
    import zipfile
    assert zipfile.is_zipfile(output_file)