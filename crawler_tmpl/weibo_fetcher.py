from requests_html import AsyncHTMLSession
from requests import Request
from loguru import logger
import asyncio
import paco
import simplejson as json
from box import Box, BoxError
from crawler_tmpl.exceptions import CaptchaError, PlatformItemError
import execjs
from crawler_tmpl.task import Task
from asyncio import Queue


start_url = 'https://m.weibo.cn/api/container/getIndex?jumpfrom=weibocom&type=uid&value=7283431349'
session = AsyncHTMLSession()


class WeiboFetcher:

    def __init__(self, platform="weibo"):
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


        if task.response is not None and not task.response.ok:
            # status codes occured so far:
            # - 418: teapot
            # - 502: proxy failed
            # - others.
            raise CaptchaError(task.original_url)

        raw_data = task.get_extras("data")
        if not raw_data:
            raw_data = task.response.json()
        elif isinstance(raw_data, str):
            raw_data = json.loads(raw_data)

        try:
            box = Box(raw_data).data.userInfo
            item = {
                "id": box.id,
                "nickname": box.screen_name,
                "avatar": box.avatar_hd,
                "desc": box.description,
                "fans": box.followers_count,
                "follows": box.follow_count,
            }
            task.parsed_result = item
            return task
        except BoxError as e:
            logger.exception(f"Parsing raw_data error: {e}, {raw_data=}")
            raise PlatformItemError(task.url, str(raw_data)) from e


    def parse_post(self, task: Task) -> Task:
        html = task.response.html
        if "出错" in html.find("title", first=True).text:
            raise PlatformItemError(task.url, html.find("body", first=True).text)

        try:
            script = html.find("script", containing="$render_data", first=True).text
            code = f"function foo() {{ {script}; return $render_data; }}; return foo();".replace(
                " var ", "; var "
            )
            data = execjs.exec_(code)
            box = Box(data["status"])
            task.parsed_result = {
                "id": box.id,
                "title": box.get("status_title"),
                "content": box.text,
                "shares": box.get("reposts_count"),
                "comments": box.get("comments_count"),
                "likes": box.get("attitudes_count"),
                "profile_url": f'https://weibo.com/u/{box.user.get("id")}',
                "profile_name": box.user.screen_name,
                "profile_avatar": box.user.avatar_hd,
                "post_time": maya.parse(box.get("created_at")).epoch,
            }
            return task
        except AttributeError as e:
            logger.error(
                f"Parse post failed: {e}, original text {task.response.html.text}"
            )
            raise e


    async def run(self, task: Task):
        task = await self.get_resp(task)
        task = await self.parse_profile(task)
        logger.info(task.parsed_result)
        