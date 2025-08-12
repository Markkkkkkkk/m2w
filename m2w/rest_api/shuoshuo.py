#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2023/2/17 4:36
# @Author  : Suzuran
# @FileName: articles.py
# @Software: PyCharm

import httpx
import math
import asyncio

async def __shuoshuo_title_request(self, client: httpx.AsyncClient, page_num: int):
    resp = await client.get(
        self.url + f"wp-json/wp/v2/shuoshuo?page={page_num}&per_page=30"
    )
    try:
        assert (
            resp.status_code == 200
        ), "Error when requiring shuoshuo lists. Please try later!"
    except AssertionError as e:
        print("Reminder from m2w: " + str(e))
        raise AssertionError

    for item in resp.json():
        self.title_dict["littleTalk"][item["title"]] = item["id"]


async def get_all_shuoshuo(self, verbose: bool) -> None:
    """
    获取所有的说说信息（带限流、超时、重试）
    """
    semaphore = asyncio.Semaphore(10)  # 每次最多并发 10 个请求

    async def fetch_with_retry(page_num, retries=3):
        for attempt in range(retries):
            try:
                async with semaphore:
                    async with httpx.AsyncClient(
                        timeout=self.timeout,
                        # proxies=self.proxies
                    ) as client:
                        await __shuoshuo_title_request(self, client, page_num)
                        return
            except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.RequestError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(2 ** attempt)  # 指数退避
                else:
                    print(f"请求失败: 第 {page_num} 页 - {e}")
                    return

    # 先获取说说总数
    async with httpx.AsyncClient(timeout=self.timeout) as client:
        resp = await client.get(self.url + "wp-json/wp/v2/shuoshuo?page=1&per_page=1")
        resp.raise_for_status()
        shuoshuo_num = int(resp.headers['x-wp-total'])

    page_num = math.ceil(shuoshuo_num / 30)

    # 并发调用每页请求
    tasks = [fetch_with_retry(page) for page in range(1, page_num + 1)]
    await asyncio.gather(*tasks)

    if verbose:
        print(f"Get shuoshuo lists complete! 共获取 {shuoshuo_num} 条说说")


