#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2023/2/17 4:36
# @Author  : Suzuran
# @FileName: categories.py
# @Software: PyCharm

import httpx
import math
import asyncio


async def __articleCategories_request(self, client: httpx.AsyncClient(), page_num: int):
    # 获取文章分类
    articleResp = await client.get(
        self.url + f"wp-json/wp/v2/categories?page={page_num}&per_page=30"
    )
    try:
        assert (
            articleResp.status_code == 200
        ), "Error when requiring category lists. Pleas try later!"
    except AssertionError as e:
        print("Reminder from m2w: " + str(e))
        raise AssertionError
    for categories in articleResp.json():
        self.categories_dict["article"][categories["name"]] = int(categories["id"])

# async def get_all_categories(self, verbose) -> None:
#     """
#     获取所有的类别信息
#     """
#     categories_num = httpx.get(
#         self.url + "wp-json/wp/v2/tags?page=1&per_page=1"
#     ).headers['x-wp-total']
#     page_num = math.ceil(float(categories_num) / 30.0)
#     async with httpx.AsyncClient() as client:
#         task_list = []
#         for num in range(1, page_num + 1):
#             req = __categories_request(self, client, num)
#             task = asyncio.create_task(req)
#             task_list.append(task)
#         await asyncio.gather(*task_list)
#     if verbose:
#         print("Get category lists complete!")
async def get_all_articleCategories(self, verbose) -> None:
    """
    获取所有的类别信息（带限流、超时、重试，保留原逻辑）
    """
    semaphore = asyncio.Semaphore(10)  # 限制并发请求数

    async def fetch_with_retry(page_num, retries=3):
        for attempt in range(retries):
            try:
                async with semaphore:
                    async with httpx.AsyncClient(
                        timeout=self.timeout,
                        # proxies=self.proxies
                    ) as client:
                        await __articleCategories_request(self,client, page_num)
                        return
            except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.RequestError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(2 ** attempt)  # 指数退避
                else:
                    print(f"请求失败: 分类第 {page_num} 页 - {e}")
                    return

    # 获取分类总数
    async with httpx.AsyncClient(timeout=self.timeout) as client:
        resp = await client.get(self.url + "wp-json/wp/v2/categories?page=1&per_page=1")
        resp.raise_for_status()
        categories_num = int(resp.headers['x-wp-total'])

    page_num = math.ceil(categories_num / 30)

    # 并发执行请求
    tasks = [fetch_with_retry(page) for page in range(1, page_num + 1)]
    await asyncio.gather(*tasks)

    if verbose:
        print(f"Get article category lists complete! 共获取 {categories_num} 个分类")



def create_articleCategory(self, category_name: str) -> int:
    """
    创建category
    @param self:
    @param category_name: 类别名
    @return: 创建category的id
    """
    try:
        resp = httpx.post(
            # proxies=self.proxies,
            timeout=self.timeout,
            url=self.url + "wp-json/wp/v2/categories",
            headers=self.wp_header,
            json={"name": category_name},
        )
        assert (
            resp.status_code == 201
        ), f"Article Category created failed. Please try again! Messages: {resp.json()['message']}"
        self.categories_dict["article"][category_name] = resp.json()['id']
        return resp.json()['id']
    except AssertionError as e:
        print("Reminder from m2w: " + str(e))

