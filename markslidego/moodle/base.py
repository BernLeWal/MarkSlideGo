"""
Moodle base class representing an (abstract) entity in Moodle backup structure
Provides methods to generate XML files for the Moodle backup
"""
import time
from abc import ABC, abstractmethod


class MoodleBase(ABC):
    """ Abstract base class for Moodle backup entities. """
    MOODLE_VERSION = "2024100705"
    MOODLE_RELEASE = "4.5.5 (Build: 20250609)"
    BACKUP_VERSION ="2024100700"
    BACKUP_RELEASE = "4.5"

    ROLE_ID = "5"
    USER_ID = "17726"


    def __init__(self):
        self.current_timestamp = int(time.time())


    def _generate_empty_(self, filename, root_elem_name, child_elem_name = None) -> None:
        file_content = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        if root_elem_name:
            file_content += f"<{root_elem_name}>\n"
        if child_elem_name:
            if isinstance(child_elem_name, list):
                for child in child_elem_name:
                    if isinstance(child, str):
                        file_content += f"  <{child}>\n"
                        file_content += f"  </{child}>\n"
            elif isinstance(child_elem_name, str):
                file_content += f"  <{child_elem_name}>\n"
                file_content += f"  </{child_elem_name}>\n"

        if root_elem_name:
            file_content += f"</{root_elem_name}>\n"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(file_content)

    @abstractmethod
    def generate(self) -> None:
        """ Generate the XML file for this Moodle entity. """
        raise NotImplementedError()
