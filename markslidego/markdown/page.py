""" Module defining a Page within a Markdown document (separated by '---'). """
import markdown
from markslidego.markdown.link import MoodleLink


class MarkdownPage:
    """ Represents a single page in a markdown presentation. """
    def __init__(self, content: str):
        self.content = content.replace('\n---', '').strip()
        self.title = self.__extract_title__()
        self.moodle_type = ""
        self.moodle_links : list[MoodleLink] = self.__extract_moodle_links__()
        self.comments = self.__extract_comments__()


    def __extract_title__(self) -> str|None:
        """ Extract the title from the markdown content. """
        for line in self.content.splitlines():
            stripped = line.strip()
            if stripped.startswith('# '):
                return stripped.lstrip('# ').strip()
            if stripped.startswith('## '):
                return stripped.lstrip('## ').strip()
            if stripped.startswith('### '):
                return stripped.lstrip('### ').strip()
        return None


    def __extract_moodle_links__(self) -> list[MoodleLink]:
        """ Extract "moodle:" links from the markdown content. """
        links = []
        for line in self.content.splitlines():
            stripped = line.strip()
            if stripped.startswith('[') and '](' in stripped:
                start = stripped.find('](moodle:')
                end = stripped.find(')', start)
                if end != -1:
                    url = stripped[start + 2:end]
                    text_start = stripped.find('[') + 1
                    text_end = stripped.find(']')
                    text = stripped[text_start:text_end]
                    link = MoodleLink(url, text)
                    links.append(link)
        return links


    def __extract_comments__(self) -> list[str]:
        """ Extract comments from the markdown content. """
        comments = []
        for line in self.content.splitlines():
            stripped = line.strip()
            if stripped.startswith('<!--') and stripped.endswith('-->'):
                comment = stripped[4:-3].strip()
                comments.append(comment)
                if comment.startswith('TYPE:'):
                    self.moodle_type = comment[len('TYPE:'):].strip()
        return comments


    def strip(self) -> str:
        """ Return content with Moodle links removed. """
        lines = []
        for line in self.content.splitlines():
            stripped = line.strip()
            if stripped.startswith('[') and '](' in stripped:
                start = stripped.find('](moodle:')
                end = stripped.find(')', start)
                if end != -1:
                    # Remove the Moodle link
                    continue
            if stripped.startswith('<!--') and stripped.endswith('-->'):
                # Remove comments
                continue
            lines.append(line)
        return '\n'.join(lines)


    @staticmethod
    def to_html(content: str) -> str:
        """ Convert the markdown content to HTML. """
        try:
            html = markdown.markdown(content)
            return html
        except ImportError:
            return "<p>Error: markdown module not installed.</p>"


    def __str__(self) -> str:
        return f"""===HTML:===
{self.to_html(self.strip())}
===
TITLE: {self.title}
MOODLE-TYPE: {self.moodle_type}
MOODLE-LINKS: {self.moodle_links}
COMMENTS: {self.comments}"""
