#!/usr/bin/env python3
"""clean_course.py

Deletes all .html, .pdf, .xml and .zip files under courses/<course-name>.
Usage: python clean_course.py <course-name>
"""

import sys
import os
from pathlib import Path

TARGET_EXTS = {'.html', '.pdf', '.xml', '.zip'}


def clean_course(course_name: str, dry_run: bool = False) -> int:
    """Walks courses/<course_name> and removes files with TARGET_EXTS.

    Returns the number of files removed (or that would be removed in dry-run).
    """
    root = Path('courses') / course_name
    if not root.exists():
        print(f"Error: {root} does not exist.")
        return 1
    if not root.is_dir():
        print(f"Error: {root} is not a directory.")
        return 2

    removed = 0
    for dirpath, dirnames, filenames in os.walk(root):
        for fname in filenames:
            p = Path(dirpath) / fname
            if p.suffix.lower() in TARGET_EXTS:
                if dry_run:
                    print(f"[DRY-RUN] Would remove: {p}")
                    removed += 1
                else:
                    try:
                        p.unlink()
                        removed += 1
                        print(f"Removed: {p}")
                    except Exception as e:
                        print(f"Failed to remove {p}: {e}")
    print(f"Done. Removed {removed} files (or would remove in dry-run).")
    return 0


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: clean_course.py <course-name> [--dry-run]")
        sys.exit(1)
    course_name = sys.argv[1]
    dry_run = '--dry-run' in sys.argv[2:]
    rc = clean_course(course_name, dry_run=dry_run)
    sys.exit(rc)
