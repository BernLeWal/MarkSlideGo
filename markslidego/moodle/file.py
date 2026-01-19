""" 
Moodle file representation for Moodle backup structure.
Provides methods to generate XML entries and handle file content for Moodle backup
"""
import hashlib
import os
import xml.etree.ElementTree as ET
import zipfile
import sys
from typing import override
from markslidego.moodle.base import MoodleBase



class MoodleFile(MoodleBase):
    """ Class to represent a Moodle file in the backup structure. """

    next_file_id = 10000
    next_context_id = 15000

    intermediate_dirs = []

    def __init__(self, filepath:str, component:str = "mod_resource", context_id:int=0, filearea:str="content"):
        super().__init__()
        self.file_id = MoodleFile.next_file_id
        MoodleFile.next_file_id += 1
        if context_id != 0:
            self.context_id = context_id
        else:
            self.context_id = MoodleFile.next_context_id
            MoodleFile.next_context_id += 1
        self.filepath = filepath
        self.subdir = ""
        self.filearea = filearea
        self.component = component

        self.filename = os.path.basename(filepath)
        self.filesize = os.path.getsize(filepath)
        self.mimetype = self.get_mime_type(filepath)
        self.creationtime = int(os.path.getctime(filepath))
        self.modificationtime = int(os.path.getmtime(filepath))

        # self.content_hash is the SHA1 hash of the file content
        sha1 = hashlib.sha1()
        with open(filepath, "rb") as f:
            while True:
                data = f.read(65536)  # Read in 64k chunks
                if not data:
                    break
                sha1.update(data)
        self.content_hash = sha1.hexdigest()

        # if file has structured content, then store them as dictionary
        self.content_dict = {}
        if self.filename == "imsmanifest.xml":
            with open(filepath, "r", encoding="utf-8") as f:
                xml_string = f.read()
            self.content_dict = self.parse_imsmanifest(xml_string)


    @staticmethod
    def get_mime_type(filepath:str) -> str:
        """ Return the mime type based on the file extension. """
        # very basic mime type detection based on file extension
        ext = os.path.splitext(filepath)[1].lower()
        if ext == ".pdf":
            return "application/pdf"
        elif ext in [".jpg", ".jpeg"]:
            return "image/jpeg"
        elif ext == ".png":
            return "image/png"
        elif ext == ".gif":
            return "image/gif"
        elif ext == ".txt":
            return "text/plain"
        elif ext == ".html" or ext == ".htm":
            return "text/html"
        elif ext == ".md":
            return "text/markdown"
        elif ext == ".zip":
            return "application/zip"
        elif ext == ".doc":
            return "application/msword"
        elif ext == ".docx":
            return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif ext == ".ppt":
            return "application/vnd.ms-powerpoint"
        elif ext == ".pptx":
            return "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        elif ext == ".xls":
            return "application/vnd.ms-excel"
        elif ext == ".xlsx":
            return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        else:
            return "application/octet-stream"  # default binary type


    @override
    def generate(self) -> None:
        """ Generate the file content in the appropriate directory structure. """
        files_subdir = self.content_hash[0:2]
        os.makedirs(f"{files_subdir}", exist_ok=True)
        os.chdir(f"{files_subdir}")
        # copy file contents to self.content_hash
        with open(self.content_hash, "wb") as out_file:
            # open source file and copy contents
            with open(os.path.join("..", "..", "..", "..", self.filepath), "rb") as in_file:
                while True:
                    data = in_file.read(65536)  # Read in 64k chunks
                    if not data:
                        break
                    out_file.write(data)
        os.chdir("..")


    def copy_file_to(self, target_dir:str) -> bool:
        """ Copy the file to the specified target directory. """
        source_filepath = os.path.join("..", "..", self.filepath)
        if os.path.exists(source_filepath):
            target_filepath = os.path.join(target_dir, self.filename)
            with open(target_filepath, "wb") as out_file:
                # open source file and copy contents
                with open(source_filepath, "rb") as in_file:
                    while True:
                        data = in_file.read(65536)  # Read in 64k chunks
                        if not data:
                            break
                        out_file.write(data)
            return True
        return False


    @staticmethod
    def parse_imsmanifest(xml_string:str) -> dict:
        """ Parse imsmanifest.xml and return a dictionary of relevant entries. """
        ns = {'imscp': 'http://www.imsglobal.org/xsd/imscp_v1p1'}
        result = {}

        try:

            root = ET.fromstring(xml_string)
            # /manifest[identifier]
            result['manifest.identifier'] = root.attrib.get('identifier')

            # /manifest/organizations/organization[identifier]
            org = root.find('imscp:organizations/imscp:organization', ns)
            result['organization.identifier'] = org.attrib.get('identifier') if org is not None else None

            # /manifest/organizations/organization/title
            org_title = org.find('imscp:title', ns) if org is not None else None
            result['organization.title'] = org_title.text if org_title is not None else None

            # /manifest/organizations/organization/item[identifier]
            item = org.find('imscp:item', ns) if org is not None else None
            result['item.identifier'] = item.attrib.get('identifier') if item is not None else None

            # /manifest/organizations/organization/item/title
            item_title = item.find('imscp:title', ns) if item is not None else None
            result['item.title'] = item_title.text if item_title is not None else None

            # /manifest/resources/resource[href]
            resource = root.find('imscp:resources/imscp:resource', ns)
            result['resource.href'] = resource.attrib.get('href') if resource is not None else None

        except ET.ParseError as e:
            print(f"Error parsing imsmanifest.xml: {e}", file=sys.stderr)
            print(xml_string, file=sys.stderr)

        return result


    @staticmethod
    def unzip_and_add(zip_filepath:str, component:str="mod_scorm") -> list:
        """ Unzip the specified zip file and create MoodleFile instances for each file inside. """
        zip_contents_dir = zip_filepath.replace(".zip", "_unzipped")
        if not os.path.exists(zip_filepath):
            print(f"Error: Zip file {zip_filepath} does not exist.", file=sys.stderr)
            return []
        with zipfile.ZipFile(zip_filepath, 'r') as zip_ref:
            zip_ref.extractall(zip_contents_dir)
        MoodleFile.intermediate_dirs.append(zip_contents_dir)

        context_id = MoodleFile.next_context_id
        MoodleFile.next_context_id += 1
        result = []
        # walk through the files in the extracted directory recursivly and create MoodleFile instances
        for root, dirs, files in os.walk(zip_contents_dir):
            for name in files:
                filepath = os.path.join(root, name)
                moodlefile = MoodleFile(filepath, component, context_id)
                if zip_contents_dir != root:
                    moodlefile.subdir = root.replace(zip_contents_dir, "")
                result.append(moodlefile)
        result.append(MoodleFile(zip_filepath, component, context_id))
        return result


    @staticmethod
    def remove_intermediate_dirs():
        """ Remove all intermediate directories created during file operations. """
        for intermediate_dir in MoodleFile.intermediate_dirs:
            if os.path.exists(intermediate_dir):
                for root, dirs, files in os.walk(intermediate_dir, topdown=False):
                    for name in files:
                        os.remove(os.path.join(root, name))
                    for name in dirs:
                        os.rmdir(os.path.join(root, name))
                os.rmdir(intermediate_dir)
