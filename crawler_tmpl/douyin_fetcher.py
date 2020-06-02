from requests_html import AsyncHTMLSession
from requests import Request
from loguru import logger
import asyncio
import paco
import simplejson as json
from box import Box
from crawler_tmpl.task import Task
from crawler_tmpl.config import config
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
        self.mappings = dict(
            [
                (z.encode("utf8").decode("unicode-escape"), k)
                for z, k in config.items("DOUYING_ICON_NUMBER_MAPPINGS")
            ]
        )

    def decode_iconfont(self, text: str) -> int:
        return int(float("".join([self.mappings[z] for z in text.split()])))

    def decode_partial_inconfont(self, text: str) -> str:
        return "".join([self.mappings.get(z, z) for z in text.split()])

    async def get_resp(self, task: Task) -> Task:
        task.response = await session.request('GET', task.url)
        await asyncio.sleep(2)
        return task

    async def parse_profile(self, task: Task) -> Task:
        try:
            html = task.response.html
            logger.debug(f"douyin response: {task.response}, html:")
        except Exception as e:
            raise e

        try:
            item = {
                "id": self.decode_partial_inconfont(
                    html.find(".shortid", first=True).text[len("抖音ID：") :]
                ),
                "follows": self.decode_iconfont(
                    html.find(".focus .num", first=True).text
                ),
                "fans": self.decode_iconfont(
                    html.find(".follower .num", first=True).text
                ),
                "likes": self.decode_iconfont(
                    html.find(".liked-num .num", first=True).text
                ),
                "nickname": html.find(".nickname", first=True).text,
                "desc": html.find(".signature", first=True).text,
                "gender": None,
                "avatar": html.find(".avatar", first=True).attrs["src"],
            }

        except AttributeError as e:
            logger.error(e)

        task.parse_result = item
        return task

    async def run(self, task: Task):
        task = await self.get_resp(task)
        logger.info(task.response.html)
        task = await self.parse_profile(task)
        logger.info(task.parse_result)
        