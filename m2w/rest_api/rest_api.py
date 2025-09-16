#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2023/2/17 0:27
# @Author  : Suzuran
# @FileName: rest_api.py
# @Software: PyCharm
import os
import asyncio
import base64

import httpx

from .articles import get_all_articles
from .shuoshuo import get_all_shuoshuo
from .tags import get_all_tags
from .articleCategories import get_all_articleCategories
from .shuoshuoCategories import get_all_shuoshuoCategories
from .update import _update_article
from .create import _create_article


class RestApi:
    def __init__(self, url: str, wp_username=None, wp_password=None):
        self.url = url if url.endswith("/") else url + "/"
        self.wp_header = {
            "Authorization": "Basic " + base64.b64encode(f"{wp_username}:{wp_password}".encode()).decode("utf-8")}
        self.title_dict = {"article": {}, "littleTalk": {}}
        self.categories_dict = {"article": {}, "littleTalk": {}}
        # 因为wordpress会把标签的别名slug都统一小写，那么不同大小写的tag他们的别名就一样的，所以这里需要记录slug然后有重复的使用之前创建的tag就可以了。
        self.tag_slug_dict = {}
        self.timeout = httpx.Timeout(connect=60.0, read=120.0, write=120.0,
                                     pool=120.0)
        # self.proxies = {  #     "http://": "http://127.0.0.1:7078",  #     "https://": "http://127.0.0.1:7078",  # }

    async def upload_article(self, md_message=None, post_metadata=None, verbose=True, force_upload=False, last_update=False, ):
        """
        自动判断更新还是创建
        @param last_update: 是否更新文章最后更新时间
        @param verbose: 是否输出控制台信息
        @param force_upload: 是否启用强制上传
        @param post_metadata: 上传文件的元信息
        @param md_message: 需要更新的md文件路径信息
        @return:
        """

        # 更新现有文章信息
        articles_async = asyncio.create_task(get_all_articles(self, verbose))
        littleTalk_async = asyncio.create_task(get_all_shuoshuo(self, verbose))
        tags_async = asyncio.create_task(get_all_tags(self, verbose))
        articleCtegories_async = asyncio.create_task(get_all_articleCategories(self, verbose))
        littleTalkCtegories_async = asyncio.create_task(get_all_shuoshuoCategories(self, verbose))

        # todo 这里获取的说说和文章title列表，来判断网站上是否已有文章，其实当我本地legacy里面md5缺失（不太可能有同名的情况，因为window电脑同文件夹不允许有重名文件），
        #  wordpress上有这个文章，本地也有这个文章，再重复上传的时候这时候只根据title来判断是否要再上传，但是不严谨，因为有可能虽然网站上和本地文件重名，但是本地已经改文件了，
        #  这时候应该按照文件内容md5来判断，但是这种本地再修改下文件再二次上传就行了，除非那种大规模本地文件缺失和legacy缺失的情况下才麻烦，所以这里先不改了。
        await articleCtegories_async
        await littleTalkCtegories_async
        await tags_async
        await articles_async
        await littleTalk_async

        md_create = md_message['new']
        md_update = md_message['legacy']

        None if not verbose else print(
            "You don't want a force uploading. The existence of the post would be checked.") if not force_upload else print(
            "You want a force uploading? Great!")

        for new_md in md_create["article"]:
            if not force_upload:
                if (os.path.basename(new_md).split('.md')[0] in self.title_dict["article"].keys()):
                    if verbose:
                        print(f'Warning: The article post {new_md} is existed in your WordPress site. Ignore uploading!')
                else:
                    if verbose:
                        print(f'The article post {new_md} is exactly a new one in your WordPress site! Try uploading...')
                    _create_article(self, md_path=new_md, post_metadata=post_metadata, )
                    if verbose:
                        print(f"The article post {new_md} uploads successful!")
            else:
                print(f"The article post {new_md} is updating")
                if (os.path.basename(new_md).split('.md')[0] in self.title_dict["article"].keys()):
                    _update_article(self, md_path=new_md, post_metadata=post_metadata, last_update=last_update, )
                else:
                    _create_article(self, md_path=new_md, post_metadata=post_metadata, )
                print(f"The article post {new_md} uploads successful!")
        for new_md in md_create["littleTalk"]:
            if not force_upload:
                if (os.path.basename(new_md).split('.md')[0] in self.title_dict["littleTalk"].keys()):
                    if verbose:
                        print(f'Warning: The littleTalk post {new_md} is existed in your WordPress site. Ignore uploading!')
                else:
                    if verbose:
                        print(f'The littleTalk post {new_md} is exactly a new one in your WordPress site! Try uploading...')
                    _create_article(self, md_path=new_md, post_metadata=post_metadata, )
                    if verbose:
                        print(f"The littleTalk post {new_md} uploads successful!")
            else:
                print(f"The littleTalk post {new_md} is updating")
                if (os.path.basename(new_md).split('.md')[0] in self.title_dict["littleTalk"].keys()):
                    _update_article(self, md_path=new_md, post_metadata=post_metadata, last_update=last_update, )
                else:
                    _create_article(self, md_path=new_md, post_metadata=post_metadata, )
                print(f"The littleTalk post {new_md} uploads successful!")
        for legacy_md in md_update["article"]:
            filename_prefix = os.path.splitext(os.path.basename(legacy_md))[0]
            if (filename_prefix in self.title_dict["article"].keys()):
                _update_article(self, md_path=legacy_md, post_metadata=post_metadata, )
                if verbose:
                    print(f"The article post {legacy_md} updates successful!")
            else:
                """这种一般是之前上传后删除了，legacy里面还有记录，然后再把本地文章修改了发布状态想重新发布，就再次上传下，或者还是删除状态，但是修改文章内容这种不重新上传,
                在create_article函数内部判断删除状态。
                """
                _create_article(self, md_path=legacy_md, post_metadata=post_metadata, )
                if verbose:
                    print(f"The article post {legacy_md} updates successful!")
                # if verbose:
                #     print(
                #         'article FAILURE to find the post. Please check your User Configuration and the title in your WordPress.')
        for legacy_md in md_update["littleTalk"]:
            filename_prefix = os.path.splitext(os.path.basename(legacy_md))[0]
            if (filename_prefix in self.title_dict["littleTalk"].keys()):
                _update_article(self, md_path=legacy_md, post_metadata=post_metadata, )
                if verbose:
                    print(f"The littleTalk post {legacy_md} updates successful!")
            else:
                _create_article(self, md_path=legacy_md, post_metadata=post_metadata, )
                if verbose:
                    print(f"The article post {legacy_md} updates successful!")
                # if verbose:
                #     print(
                #         ' littleTalk FAILURE to find the post. Please check your User Configuration and the title in your WordPress.')
