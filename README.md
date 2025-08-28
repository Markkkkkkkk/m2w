

# Preface

We mentioned before that the workflow of the blog is to write a markdown file locally in Typora, and then synchronize it to wordpress through the m2w tool interface. And today we will introduce the use of M2W tools.

m2w I modified it based on [this project] (https://github.com/huangwb8/m2w) (based on v2.5.12 version), and added the functions I wanted on this basis:

1. Add restAPI and account password to staus:delete to permanently delete articles.
2. Realize the addition, deletion and modification of the statement. Implement the acquisition and creation of the classification.
3. Save the talk and the article legacy separately. In this way, there is no need to worry about the problem of duplicate names with the article.
4. Optimized the interface for asynchronously obtaining categories, tags, articles, and talk lists. It will not be too old to report the wrong timeout.

The modified m2w can be found here: [Github] (https://github.com/Markkkkkkkk/m2w), [Gitee] (https://gitee.com/markk/m2w); Next, we will introduce how to use M2W after the magic change.

All m2w versions rely on xmlrcp.php, so don't turn off its API for your WordPress site (open by default). In the era of WordPress 6.0, with Wordfence, there is actually no need to worry too much about security issues. It is recommended to use m2w when the site has https, otherwise it may cause account/password leakage (if the blog only has http, it is recommended to use https; You can see [this article] (https://hyly.net/categroy/article/code/wordpress/353/#header-id-22)).

# Regular use

## application_password Acquisition

Get the 'application_password' first:

If you are using a security plugin like wordfence, enable WordPress application passwords:

! [img] (https://image.hyly.net/i/2025/08/27/321ec1832fe1efcf00877b69ab4f6297-0.webp)

Create a new REST API:

! [img] (https://image.hyly.net/i/2025/08/28/6c428375bc39e3d183bdacc44bb67314-0.webp)

Keep the API safe. If necessary, you can regenerate or delete:

! [img] (https://image.hyly.net/i/2025/08/28/34a04329512a0c8278c2b8652527edbd-0.webp)

## Software Download

Find the software package in the Release on [Github] (https://github.com/Markkkkkkkk/m2w) or [Gitee] (https://gitee.com/markk/m2w):

! [image-20250828150957356] (https://image.hyly.net/i/2025/08/28/cef5349c13219b9913b906fa0bee788c-0.webp)

! [image-20250828151014532] (https://image.hyly.net/i/2025/08/28/f8e0741d5e828cc7dba3b30a27378c06-0.webp)

Download it and then unzip it, first modify the 'config/user.json' file:

! [image-20250828151239260] (https://image.hyly.net/i/2025/08/28/6e43e2196dbe8e6b2e8edf9ff7cc7e83-0.webp)

After the modification is completed, open the 'run_blog_and_git.bat' file in Notepad to modify the corresponding part:

! [image-20250828151632057] (https://image.hyly.net/i/2025/08/28/c8ce3add01fc8c504d3a34d6780c4ecc-0.webp)

After the above two files are modified, save them, and directly execute 'run_blog_and_git.bat' to automatically upload the article to wordpress and save the latest article to git, so that the original article sample will not be lost, and it is convenient to view the article modification record.

When you write Typora articles in the future, it is also recommended to add 'YAML Front Matter' at the beginning, which is something like this:

! [image-20250828155147169] (https://image.hyly.net/i/2025/08/28/245e5eb47ddb186d02120cd956f6ebac-0.webp)

It needs to be written at the beginning of the article, and it doesn't work to use this syntax anywhere else. Specifically, it is written like this:

```
---
category: [Blog Builder]
tag: [Server Settings, SSH Key Login, Fail2ban, Website Security, wordfence, WPS Hide Login, CloudFlare]
postType: post
status: publish
---
```

1. Category:Article/Talk about the name of the category. You can write more than one, but it is recommended to write only one, tags can be written as several. If wordpress does not have a category, it will create a category, and if there is, it will divide the existing category.
2. tag: The tag of the article/talk can be written as many as one. If wordpress doesn't have this tag, it will create a tag, and if it does, it will paste an existing tag.
3. postType: The publish type. post is the article, shuoshuo is the release of the story.
4. status: The status of the article. publish will publish to wordpress when running m2w, draft will not publish wordpress. (delete will delete the article of the same name on wordpress/talk, use it with caution, and you need to turn on the deletion function below.) ）

# Source code download

If you want to see the source code and make magic changes again, you can directly download the source code to customize the settings. It is recommended to use [Miniconda](https://gitee.com/link?target=https%3A%2F%2Fdocs.conda.io%2Fen%2Flatest%2Fminiconda.html) to manage Python versions and related dependencies, and [Pycharm]( https://www.jetbrains.com/pycharm/) Tools to modify the code, which are the required dependencies:

```
# Python version requirements
python_requires='>=3.7.6'

# Dependencies
install_requires=[
    "python-frontmatter>=1.0.0",
    "markdown>=3.3.6",
    "python-wordpress-xmlrpc>=2.3",
    "httpx>=0.24.0"
]
```

It should be noted that in later versions, I think it is a bit too dangerous for m2w to directly control the deletion of articles, and this is not a high-frequency operation, so the function of deleting articles/talking by setting the status of 'status:delete' is banned. If you want to have this function, you can download the source code to undo this comment, the directory location is 'm2w/rest_api/update.py:90' here:

! [image-20250828154659658] (https://image.hyly.net/i/2025/08/28/e88cef122909357441384bfdd6cf26d0-0.webp)

# Summary

The configuration of m2w is not too difficult to use, if you have any questions or feel that you want to add some functions that everyone likes, please leave a message below, and you will consider adding the most popular function~
