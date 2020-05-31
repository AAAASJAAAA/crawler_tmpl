from crawler_tmpl.task import Task
from crawler_tmpl.xhs_main import Fetcher

import paco
from requests_html import AsyncHTMLSession

start_url = 'https://www.xiaohongshu.com/discovery/item/5ebac8aa000000000100240a'
session = AsyncHTMLSession()


if __name__ == '__main__':
    task = Task()
    fetch = Fetcher()
    paco.run(fetch.run(task))