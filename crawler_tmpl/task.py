# start_url = 'https://www.xiaohongshu.com/discovery/item/5ebac8aa000000000100240a'
start_url = 'https://www.xiaohongshu.com/user/profile/5990bfe35e87e72c8c9d8d7c'

class Task:

    def __init__(self, url=start_url):
        self.response = None
        self.parse_result = None
        self.url = url
        self.extras = None

    @classmethod
    def build_from_url(cls, url):
        return cls(url)

    def get_extras(self, key):
        return (self.extras or {}).get(key)
