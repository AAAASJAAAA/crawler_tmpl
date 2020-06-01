from requests_html import AsyncHTMLSession
from requests import Request
from loguru import logger
import asyncio
import paco
import simplejson as json
from box import Box
from crawler_tmpl.task import Task
from asyncio import Queue



# start_url = 'https://www.xiaohongshu.com/discovery/item/5ebac8aa000000000100240a'
start_url = 'https://www.xiaohongshu.com/user/profile/5990bfe35e87e72c8c9d8d7c'
session = AsyncHTMLSession()


class Fetcher:

    def __init__(self, platform="xiaohongshu"):
        self.session = session
        self.platform = platform
        self.start_url = start_url
        self.tasks = []
        self.sid = 0


    async def get_resp(self, task: Task) -> Task:
        task.response = await session.request('GET', task.url)
        await asyncio.sleep(5)
        return task

    def _get_json_content(self, task: Task) -> str:
        content = task.response.html.find('script')[-1].text[
            len('window.__INITIAL_SSR_STATE__='):
        ]
        return content.replace("undefined", "null")

    def _get_box(self, content) -> Box:
        box = Box(json.loads(content))
        if "ErrorPage" in box:
            asyncio.sleep(3)
            raise PlatformItemError(box.ErrorPage.info)
        return box
        
    def standarize_xhs_images(self, url: str) -> str:
        if url.startswith("//ci.xiaohongshu.com"):
            return "https:" + url
        return url


    async def run(self, task: Task):
        while True:
            try:
                task = await self.get_resp(task)
                if 'profile' in task.url:
                    self.parse_profile(task)
                if 'discover' in task.url:
                    self.parse_post(task)
                    self.extract_post_links(task)
                task = await self.get_task()
            except Exception as e:
                logger.error(e)


    def extract_post_links(self, task):
        content = self._get_json_content(task) 
        notes = self._get_box(content).NoteView.panelData
        for note in notes:
            new_task = Task.build_from_url(
                f"https://www.xiaohongshu.com/discovery/item/{note.id}"
            )
            self.tasks.append(new_task)
        return self.tasks

    async def get_task(self) -> Task:
        self.sid += 1
        return self.tasks[self.sid]


    def parse_post(self, task: Task) -> dict:
        content = self._get_json_content(task)
        logger.info(content)
        box = self._get_box(content).NoteView.noteInfo
        author_url_tmpl = 'https://www.xiaohongshu.com/user/profile/{}'
        normal_post_url_tmpl = 'https://www.xiaohongshu.com/discovery/item/{}'

        new_profile_task = Task.build_from_url(author_url_tmpl)
        self.tasks.append(new_profile_task)

        item = {
            "id": box.id,
            "real_url": normal_post_url_tmpl.format(box.id),
            "title": box.title or box.generatedTitle,
            "images": [self.standarize_xhs_images(img.url) for img in box.imageList],
            "desc": box.desc,
            "comments": box.comments,
            "likes": box.likes,
            "favs": box.collects,
            "user_id": box.user.id,
            'profile_url': author_url_tmpl.format(box.user.id),
            'profile_avatar': box.user.image,
            'profile_name': box.user.nickname,
            "post_time": box.time,
        }

        task.parse_result = item


        logger.info(f'{item=}')
        write_data(item)
        return item

    def parse_profile(self, task: Task) -> dict:
        content = self._get_json_content(task)
        logger.info(content)
        box = self._get_box(content)
        user_detail = box.Main.userDetail
        for note in  box.Main.notesDetail:
            new_task = Task.build_from_url(
                f"https://www.xiaohongshu.com/discovery/item/{note.id}"
            )
            self.tasks.append(new_task)

        item = {
            "id": user_detail.id,
            "nickname": user_detail.nickname,
            "avatar": user_detail.image,
            "desc": user_detail.desc,
            "fans": user_detail.fans,
            "follows": user_detail.follows,
            "likes": user_detail.liked,
            "favs": user_detail.collected,
            "gender": user_detail.gender,
        }

        task.parse_result = item

        logger.info(f'{item=}')
        write_profile_data(item)

        return item



def write_data(item: dict):
    with open('data.json', 'a+') as f:
        f.write(json.dumps(item) + '\n')


def write_profile_data(item: dict):
    with open('profile_data.json', 'a+') as f:
        f.write(json.dumps(item) + '\n')