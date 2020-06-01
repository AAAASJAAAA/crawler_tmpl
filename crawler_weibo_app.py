from crawler_tmpl.task import Task
from crawler_tmpl.weibo_fetcher import WeiboFetcher

import paco 

profile_url = 'https://weibo.com/u/7283431349'



if __name__ == "__main__":
    task = Task(profile_url)
    wfetcher = WeiboFetcher()
    paco.run(wfetcher.run(task))

