import aioredis
import asyncio
from aiohttp import ClientSession, ClientTimeout
from aiohttp import client_exceptions
from fake_useragent import UserAgent

import random
import re
import os
import traceback
from typing import Callable


class ProxyPool:
    """
    Tables in Redis DB:
        proxies: set of proxy addresses.
        frozen: set of proxies which used at current moment.
    """
    DB = "redis://127.0.0.1:6379"
    SOURCES = {
        "clarketm_proxies": "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list.txt",
    }

    def __init__(self, loop: asyncio.BaseEventLoop = None):
        self.loop = loop if loop else asyncio.get_event_loop()
        self.is_result = False

    async def upload_proxies(self):
        redis_pool = await aioredis.create_redis_pool(self.DB)
        old_proxies = await redis_pool.smembers("proxies", encoding="utf-8")

        async with ClientSession() as session:
            try:
                for sourcename, url in self.SOURCES.items():
                    if sourcename == "clarketm_proxies":
                        async with session.get(url) as response:
                            data = await response.text()

                        proxies = re.findall(r"(\d+\.\d+\.\d+\.\d+:\d+).*-S", data)
                        random.shuffle(proxies)
                        new_proxies = list(set(proxies) - set(old_proxies))
                        if new_proxies:
                            await redis_pool.sadd("proxies", *new_proxies)

            except Exception:
                print(traceback.format_exc())

        redis_pool.close()
        await redis_pool.wait_closed()

    def run(self, future):
        self.loop.run_until_complete(future)
        self.loop.close()

    async def create_redis_pool(self):
        return await aioredis.create_redis_pool(self.DB)

    async def insert_proxies(self, proxies: list, redis_pool=None):
        if not redis_pool:
            redis_pool = await aioredis.create_redis_pool(self.DB)

        await redis_pool.sadd('proxies', *proxies)

        if not redis_pool:
            redis_pool.close()
            await redis_pool.wait_closed()

    async def get_random_proxies(self, count=20, redis_pool=None):
        if not redis_pool:
            redis_pool = await aioredis.create_redis_pool(self.DB)

        proxies = await redis_pool.srandmember(key='proxies', count=count, encoding='utf-8')
        frozen_proxies = await redis_pool.smembers(key='frozen')

        if not redis_pool:
            redis_pool.close()
            await redis_pool.wait_closed()

        return list(set(proxies) - set(frozen_proxies))

    async def block_proxy(self):
        pass

    async def pool_post(self, url, data, answer_middleware: Callable = None):
        redis_pool = await aioredis.create_redis_pool(self.DB)
        task = self.loop.create_task(self.get_random_proxies(redis_pool=redis_pool))
        proxies = await task
        print(f'processing with {len(proxies)} proxies')

        async with ClientSession() as session:
            tasks = [
                asyncio.ensure_future(
                    self.post(
                        session=session, url=url, data=data,
                        proxy=proxy,
                        redis_pool=redis_pool,
                        custom_middleware=answer_middleware
                    )
                )
                for proxy in proxies
            ]
            responses = await asyncio.gather(*tasks)

        redis_pool.close()
        await redis_pool.wait_closed()

        return responses

    async def post(self, session, url: str, data, proxy: str, redis_pool, custom_middleware: Callable = None):
        await redis_pool.sadd('frozen', proxy)

        try:
            http_proxy = 'http://'+proxy if not proxy.startswith('http://') else proxy
            ua = UserAgent()
            async with session.post(url=url, data=data, params={'User-Agent': ua.random},
                                    proxy=http_proxy,
                                    timeout=ClientTimeout(15)) as response:
                if 'captcha' in str(response.url):                 # Usecase for requests to cian.ru
                    await redis_pool.srem('proxies', proxy)
                else:
                    if not self.is_result and custom_middleware:
                        self.is_result = True
                        await custom_middleware(response)

                result = response

        except (client_exceptions.ServerDisconnectedError,
                client_exceptions.ClientOSError,                   # Connection reset by peer
                client_exceptions.ClientHttpProxyError,
                client_exceptions.ContentTypeError,
                asyncio.exceptions.TimeoutError):
            result = None

        await redis_pool.srem('frozen', proxy)
        return result


async def test_middleware(response):
    d = await response.json()
    print(d)


if __name__ == '__main__':
    pass




