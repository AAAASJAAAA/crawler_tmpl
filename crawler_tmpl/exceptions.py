class CrawlerTmplError(Exception):
    """BaseError for all bad things happened in the project"""


class PlatformItemError(CrawlerTmplError):
    """Raise if it's deleted remotely or under review"""
    def  __init__(self, info):
        self.info = info

    def __str__(self):
        return f'platform item error: {self.info}'


class CaptchaError(CrawlerTmplError):
    """Raise when meet captcha"""
    def __init__(self, url):
        self.url = url

    def __str__(self):
        return f"CAPTCHA: {self.url}"
