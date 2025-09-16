#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2023/2/17 17:35
# @Author  : Suzuran
# @FileName: create.py
# @Software: PyCharm

from .tags import create_tag
from .articleCategories import create_articleCategory
from .shuoshuoCategories import create_custom_taxonomy_term
import frontmatter
import markdown
import os
import httpx


def _create_article(self, md_path, post_metadata) -> None:
    """
    创建文章
    @param md_path: md文件路径
    @param post_metadata: 上传文件的元信息
    @return:
    """
    filename = os.path.basename(md_path)

    try:
        assert filename.split('.')[-1] == "md", "Only files with suffix .md supported!"
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
    postType = post_metadata["postType"]
    for tag in post_metadata["tag"]:
        # 如果已经存在同名小写slug则把ID赋值，否则用tag名字重新创建。
        tagSlug=tag.lower()
        if tagSlug in self.tag_slug_dict.keys():
            tags.append(self.tag_slug_dict[tagSlug])
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
        "status": post_metadata["status"],
        "comment_status": "open",
        "categories": categories,
        "tags": tags,
    }
    resp=None
    if (postType == "shuoshuo" and post_metadata["status"] == "publish"):
        # 如果是说说把内容转成HTML，这样markdown能正常显示
        resp = httpx.post(
            # proxies=self.proxies,
            timeout=self.timeout,
            url=self.url + "wp-json/wp/v2/shuoshuo",
            headers=self.wp_header,
            json=post_data,
        )
    elif (postType == "post" and post_metadata["status"] == "publish"):
        resp = httpx.post(
            # proxies=self.proxies,
            timeout=self.timeout,
            url=self.url + "wp-json/wp/v2/posts",
            headers=self.wp_header,
            json=post_data,
        )
    # try:
    #     assert (
    #         resp.status_code == 201
    #     ), f"File {md_path} uploaded failed. Please try again!"
    # except AssertionError as e:
    #     print("Reminder from m2w: " + str(e))
    #     raise AssertionError

    try:
        # 说说200是成功，文章201是成功
        if resp==None:
            print(f"删除状态下修改无需上传。")
        elif resp.status_code != 200 and resp.status_code != 201:
            print(f"上传失败，状态码：{resp.status_code}")
            print("响应内容：", resp.text.encode('utf-8').decode('unicode_escape'))
            raise AssertionError(f"File {md_path} uploaded failed. Please try again!")
    except AssertionError as e:
        print("Reminder from m2w: " + str(e))
        raise
