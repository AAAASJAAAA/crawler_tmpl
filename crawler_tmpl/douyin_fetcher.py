from requests_html import AsyncHTMLSession
from requests import Request
from loguru import logger
import asyncio
import paco
import simplejson as json
from box import Box
from crawler_tmpl.task import Task
from asyncio import Queue



start_url = 'https://www.iesdouyin.com/share/user/3496035207873751'
session = AsyncHTMLSession()


class DouyinFetcher:

    def __init__(self, platform="douyin"):
        self.session = session
        self.platform = platform
        self.start_url = start_url
        self.tasks = []
        self.sid = 0


    async def get_resp(self, task: Task) -> Task:
        task.response = await session.request('GET', task.url)
        await asyncio.sleep(2)
        return task

    async def parse_profile(self, task: Task) -> Task:
        try:
            html = task.response.html
            logger.debug(f"douyin response: {task.response}, html:")
        except Exception as e:
            logger.error(e)


    async def run(self, task: Task):
        task = await self.get_resp(task)
        logger.info(task.response.html)
        