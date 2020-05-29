

class Task:

    def __init__(self, url=start_url):
        self.response = None
        self.parse_result = None
        self.url = url

    @classmethod
    def build_from_url(cls, url):
        return cls(url)

