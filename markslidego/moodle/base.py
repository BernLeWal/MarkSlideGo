"""
Moodle base class representing an (abstract) entity in Moodle backup structure
Provides methods to generate XML files for the Moodle backup
"""
import time
from abc import ABC, abstractmethod


class MoodleBase(ABC):
    def __init__(self):
        self.MOODLE_VERSION = "2024100705"
        self.MOODLE_RELEASE = "4.5.5 (Build: 20250609)"
        self.BACKUP_VERSION ="2024100700"
        self.BACKUP_RELEASE = "4.5"

        self.ROLE_ID = "5"
        self.USER_ID = "17726"

        self.current_timestamp = int(time.time())


    def _generate_empty_(self, filename, rootElemName, childElemName = None) -> None:
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

    @abstractmethod
    def generate(self) -> None:
        raise NotImplementedError()

