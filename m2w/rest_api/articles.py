#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2023/2/17 4:36
# @Author  : Suzuran
# @FileName: articles.py
# @Software: PyCharm

import httpx
import math
import asyncio


async def __article_title_request(self, client: httpx.AsyncClient(), page_num: int):
    resp = await client.get(
        self.url + f"wp-json/wp/v2/posts?page={page_num}&per_page=30"
    )
    try:
        assert (
            resp.status_code == 200
        ), "Error when requiring article lists. Pleas try later!"
    except AssertionError as e:
        print("Reminder from m2w: " + str(e))
        raise AssertionError

    for article in resp.json():
        self.title_dict["article"][article["title"]["rendered"]] = article['id']


# async def get_all_articles(self, verbose) -> None:
#     """
#     获取所有的文章信息
#     """
#     article_num = httpx.get(self.url + "wp-json/wp/v2/posts?page=1&per_page=1").headers[
#         'x-wp-total'
#     ]
#     page_num = math.ceil(float(article_num) / 30.0)
#     async with httpx.AsyncClient() as client:
#         task_list = []
#         for num in range(1, page_num + 1):
#             req = __article_title_request(self, client, num)
#             task = asyncio.create_task(req)
#             task_list.append(task)
#         await asyncio.gather(*task_list)
#     if verbose:
#         print("Get article lists complete!")
async def get_all_articles(self, verbose) -> None:
    """
    获取所有的文章信息（带限流、超时、重试，保留原逻辑）
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
                        # 直接调用你原来的方法
                        await __article_title_request(self,client, page_num)
                        return
            except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.RequestError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(2 ** attempt)  # 指数退避
                else:
                    print(f"请求失败: 第 {page_num} 页 - {e}")
                    return

    # 先获取文章总数
    async with httpx.AsyncClient(timeout=self.timeout) as client:
        resp = await client.get(self.url + "wp-json/wp/v2/posts?page=1&per_page=1")
        resp.raise_for_status()
        article_num = int(resp.headers['x-wp-total'])

    page_num = math.ceil(article_num / 30)

    # 并发调用每页请求
    tasks = [fetch_with_retry(page) for page in range(1, page_num + 1)]
    await asyncio.gather(*tasks)

    if verbose:
        print(f"Get article lists complete! 共获取 {article_num} 篇文章")

