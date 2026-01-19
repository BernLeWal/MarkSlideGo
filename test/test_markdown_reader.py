# python
import os
import sys
from pathlib import Path
import pytest

# Ensure repository root is on sys.path so tests can import the package reliably
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from markslidego.markdown.reader import MarkdownReader
from markslidego.markdown.page import MarkdownPage


@pytest.fixture(autouse=True)
def use_tmp_cwd(tmp_path):
    """Change working directory to a temporary path for each test and clean up."""
    old_cwd = os.getcwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(old_cwd)


def test_nonexistent_file_reports_error_and_sets_defaults(capsys, tmp_path):
    p = tmp_path / "no-such-file.md"
    reader = MarkdownReader(str(p))
    captured = capsys.readouterr()
    assert "does not exist" in captured.out
    assert reader.content == ""
    assert reader.pages == []
    assert reader.metadata == {}
    assert reader.is_marp is False


def test_frontmatter_parsing_and_page_split(tmp_path):
    md = """---
title: "Test Title"
marp: true
draft: false
author: 'Alice'
# this is a comment
invalidlinewithoutcolon
---
# Slide 1
Content A

---
# Slide 2
Content B
"""
    path = tmp_path / "with_frontmatter.md"
    path.write_text(md, encoding="utf-8")

    reader = MarkdownReader(str(path))

    # metadata parsing
    assert reader.metadata.get("title") == "Test Title"
    assert reader.metadata.get("marp") is True
    assert reader.metadata.get("draft") is False
    assert reader.metadata.get("author") == "Alice"
    # commented and invalid lines should be ignored
    assert "invalidlinewithoutcolon" not in reader.metadata

    # is_marp set
    assert reader.is_marp is True

    # pages should be created from content after frontmatter
    assert isinstance(reader.pages, list)
    assert len(reader.pages) == 2
    assert all(isinstance(p, MarkdownPage) for p in reader.pages)

    # content should equal full file text (final re-read)
    assert reader.content == md


def test_no_frontmatter_pages_not_created_but_content_read(tmp_path):
    # File without frontmatter but with separators in body
    md = """# Slide A
Body A

---
# Slide B
Body B
"""
    path = tmp_path / "no_frontmatter.md"
    path.write_text(md, encoding="utf-8")

    reader = MarkdownReader(str(path))

    # Due to current implementation, if no leading frontmatter markers are found,
    # the initial read consumes the file and pages are not created.
    assert reader.pages == []

    # content should still be the full file after final read
    assert reader.content == md


def test_with_lesson_markdonw_file(tmp_path):
    # use the provided test-lesson.md content from the /test directory - not the tmp_path
    test_lesson_path = Path(__file__).parent / "test-lesson.md"
    reader = MarkdownReader(str(test_lesson_path))
    print(f"Metadata: \n{reader.metadata}")
    assert reader.metadata.get("title") != ""
    print(f"Is Marp: {reader.is_marp}")
    print(f"Content: {len(reader.content)} characters")
    assert len(reader.content) > 0
    print(f"Pages: {len(reader.pages)} pages")
    assert len(reader.pages) > 0
    print(f"First page content:\n{reader.pages[0] if reader.pages else 'No pages found.'}")
    print(f"Last page content:\n{reader.pages[-1] if reader.pages else 'No pages found.'}")
