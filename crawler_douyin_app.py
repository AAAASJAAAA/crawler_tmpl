from crawler_tmpl.task import Task
from crawler_tmpl.douyin_fetcher import DouyinFetcher

import paco 

profile_url = 'https://www.iesdouyin.com/share/user/3496035207873751'



if __name__ == "__main__":
    task = Task(profile_url)
    douyin_fetcher = DouyinFetcher()
    paco.run(douyin_fetcher.run(task))

