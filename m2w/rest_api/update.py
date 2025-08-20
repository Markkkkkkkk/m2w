#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2023/2/17 17:35
# @Author  : Suzuran
# @FileName: update.py
# @Software: PyCharm

from .articleCategories import create_articleCategory
from .shuoshuoCategories import create_custom_taxonomy_term
from .tags import create_tag
import frontmatter
import markdown
import os
import httpx
import time


def _update_article(self, md_path, post_metadata, last_update=False) -> None:
    """
    更新文章
    @param md_path: md文件路径
    @param post_metadata: 上传文件的元信息
    @return:
    """

    filename = os.path.basename(md_path)
    filename_prefix, filename_suffix = os.path.splitext(
        filename
    )

    try:
        assert filename_suffix == ".md", "Only files with suffix .md supported!"
    except AssertionError as e:
        print("Reminder from m2w: " + str(e))
        raise AssertionError

    # 1 通过frontmatter.load函数加载读取文档里的信息，包括元数据
    post_from_file = frontmatter.load(md_path)

    # 2 markdown库导入内容
    post_content_html = markdown.markdown(
        post_from_file.content, extensions=['markdown.extensions.fenced_code']
    )
    post_content_html = post_content_html.encode("utf-8")

    # 3 将本地post的元数据暂存到metadata中
    metadata_keys = post_metadata.keys()
    for key in metadata_keys:
        if (
                key in post_from_file.metadata
        ):  # 若md文件中没有元数据'category'，则无法调用post.metadata['category']
            post_metadata[key] = post_from_file.metadata[key]

    # 4 更新tag和category的id信息
    tags = []
    categories = []
    status = post_metadata["status"]
    postType = post_metadata["postType"]
    for tag in post_metadata["tag"]:
        if tag in self.tags_dict.keys():
            tags.append(self.tags_dict[tag])
        else:
            tags.append(create_tag(self, tag))
    for category in post_metadata["category"]:
        if (postType == "shuoshuo"):
            if category in self.categories_dict["littleTalk"].keys():
                categories.append(self.categories_dict["littleTalk"][category])
            else:
                categories.append(create_custom_taxonomy_term(self, "shuoshuo_category", category))
        else:
            if category in self.categories_dict["article"].keys():
                categories.append(self.categories_dict["article"][category])
            else:
                categories.append(create_articleCategory(self, category))
    # 5 构造上传的请求内容
    post_data = {
        "title": filename.split(".md")[0],
        "content": str(post_content_html, encoding="utf-8"),
        "status": status,
        "categories": categories,
        "tags": tags,
    }

    if last_update:
        post_data['date'] = (
            time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(time.time())),
        )
    # 删除文章:force=false（默认）	文章会进入回收站，可恢复  force=true 彻底删除文章，无法恢复
    if (status == 'delete'):
        print("接口删除文章太危险，请登录wordpress后台手动删除说说/文章。")
        # if (postType == "shuoshuo"):
        #     resp = httpx.delete(
        #         # proxies=self.proxies,
        #         # url=self.url
        #         # + f"wp-json/wp/v2/posts/{self.article_title_dict[os.path.basename(md_path).strip('.md')]}",
        #         url=self.url
        #             + f"wp-json/wp/v2/shuoshuo/{post_data['title']}",
        #         timeout=self.timeout,
        #         headers=self.wp_header
        #     )
        # else:
        #     resp = httpx.delete(
        #         timeout=self.timeout,
        #         # proxies=self.proxies,
        #         # url=self.url
        #         # + f"wp-json/wp/v2/posts/{self.article_title_dict[os.path.basename(md_path).strip('.md')]}",
        #         url=self.url
        #             + f"wp-json/wp/v2/posts/{self.title_dict['article'][filename_prefix]}?force=true",
        #         headers=self.wp_header
        #     )
    else:
        if (postType == "shuoshuo"):
            resp = httpx.put(
                timeout=self.timeout,
                # proxies=self.proxies,
                url=self.url
                    + "wp-json/wp/v2/shuoshuo",
                headers=self.wp_header,
                json=post_data,
            )
        else:
            # 更新文章
            resp = httpx.post(
                timeout=self.timeout,
                # proxies=self.proxies,
                # url=self.url
                # + f"wp-json/wp/v2/posts/{self.article_title_dict[os.path.basename(md_path).strip('.md')]}",
                url=self.url
                    + f"wp-json/wp/v2/posts/{self.title_dict['article'][filename_prefix]}",
                headers=self.wp_header,
                json=post_data,
            )
    try:
        # 说说200是成功，文章201是成功
        if resp.status_code != 200 and resp.status_code != 201:
            print(f"上传失败，状态码：{resp.status_code}")
            print("响应内容：", resp.text)
            raise AssertionError(f"File {md_path} uploaded failed. Please try again!")
    except AssertionError as e:
        print("Reminder from m2w: " + str(e))
        raise
