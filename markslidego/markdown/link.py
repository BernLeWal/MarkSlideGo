""" Module to represent links in markdown files. """

class Link:
    """ Class to represent a (general) link. """
    def __init__(self, url: str, text: str) -> None:
        self.url = url
        self.text = text


    def __str__(self) -> str:
        return f"[{self.text}]({self.url})"
    def __repr__(self) -> str:
        return f"[{self.text}]({self.url})"


class MoodleLink(Link):
    """ Class to represent a Moodle-specific link (starts with "moodle://") """
    def __init__(self, url: str, text: str) -> None:
        super().__init__(url, text)
        self.type = ""
        self.params: dict[str, str] = {}
        self.__parse_url__()


    def __parse_url__(self) -> None:
        """ Parse the Moodle link URL to extract type and parameters. """
        if self.url.startswith("moodle://"):
            parts = self.url[len("moodle://"):].split("?")
            self.type = parts[0]
            if len(parts) > 1:
                param_str = parts[1]
                param_pairs = param_str.split("&")
                for pair in param_pairs:
                    if "=" in pair:
                        key, value = pair.split("=", 1)
                        self.params[key] = value


    def __str__(self) -> str:
        return f"[{self.text}](moodle:{self.type}?{self.params})"
    def __repr__(self) -> str:
        return f"MoodleLink(text={self.text}, type={self.type}, params={self.params})"
