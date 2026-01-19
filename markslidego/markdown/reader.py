""" Module to read and parse markdown files. """
import os

from markslidego.markdown.page import MarkdownPage


class MarkdownReader:
    """ Class to read and parse markdown files. """

    MAX_METADATA_LINES = 30

    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.metadata: dict[str, str] = {}
        self.is_marp: bool = False
        self.is_moodle: bool = False
        self.content: str = ""
        self.pages: list[MarkdownPage] = []

        self.__read__()


    def __read__(self) -> None:
        """ Read the markdown file and store its content. """
        if not os.path.exists(self.filepath):
            # log error
            print(f"Error: File '{self.filepath}' does not exist.")
            return None

        frontmatter = []
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:

                # Read meta-data
                inside = False
                for i in range(self.MAX_METADATA_LINES):
                    line = f.readline()
                    if line == '':
                        break
                    stripped = line.strip()
                    if stripped == '---':
                        if not inside:
                            inside = True
                            continue
                        else:
                            # end of frontmatter
                            break
                    if inside:
                        frontmatter.append(stripped)

                self.content = f.read()

                # if content is not empty, then split into pages using '---' as separator
                if self.content.strip():
                    self.pages = [MarkdownPage(page.strip()) for page in self.content.split('\n---\n')]
        except Exception:
            return None

        if frontmatter:
            # Parse metadata
            for ln in frontmatter:
                if not ln or ln.startswith('#'):
                    continue
                if ':' not in ln:
                    # skip invalid lines
                    continue
                key, val = ln.split(':', 1)
                key = key.strip()
                val = val.strip()
                # remove surrounding quotes if present
                if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                    val = val[1:-1]
                # convert booleans
                if val.lower() == 'true':
                    parsed_val = True
                elif val.lower() == 'false':
                    parsed_val = False
                else:
                    parsed_val = val
                self.metadata[key] = parsed_val
                if key == 'marp' and parsed_val is True:
                    self.is_marp = True
                if key == 'moodle' and parsed_val is True:
                    self.is_moodle = True

        with open(self.filepath, 'r', encoding='utf-8') as f:
            self.content = f.read()


    @staticmethod
    def get_md_info(md_file:str) -> dict|None:
        """ Read the top of a markdown file and extract title and description."""
        info = {}
        if os.path.exists(md_file):
            try:
                first_line = ""
                with open(md_file, 'r', encoding='utf-8') as f:
                    while line := f.readline():
                        line = line.strip()
                        if first_line == "" and line:
                            first_line = line.lstrip("# ").strip()
                            info['title'] = first_line
                            info['description'] = ""
                        elif line.startswith("# "):
                            return info # next section, stop processing
                        else: # add to description
                            info['description'] = info['description'] + line.strip() + "\n"
            except Exception:
                pass
        return info
