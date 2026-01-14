import os
import time


class MoodleBase:
    def __init__(self):
        self.MOODLE_VERSION = "2024100705"
        self.MOODLE_RELEASE = "4.5.5 (Build: 20250609)"
        self.BACKUP_VERSION ="2024100700"
        self.BACKUP_RELEASE = "4.5"

        self.ROLE_ID = "5"
        self.USER_ID = "17726"

        self.current_timestamp = int(time.time())


    def generate_empty(self, filename, rootElemName, childElemName = None) -> None:
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