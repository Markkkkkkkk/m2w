

# 前言

之前我们有提到博客的工作流是本地用Typora编写markdown文件，然后通过m2w工具接口同步到wordpress里面去。而今天我们就来介绍下m2w工具的使用。

m2w我是根据[这个项目](https://github.com/huangwb8/m2w)魔改而来（基于v2.5.12版本），在此基础上增加了自己想要的功能：

1. 增加restAPI 和账号密码添加staus:delete 可以永久删除文章。
2. 实现说说的增删改。实现说说分类获取和创建。
3. 把说说和文章legacy分开储存。这样就不用担心说说和文章重名的问题。
4. 优化异步获取分类，标签，文章，说说列表接口。不至于老报错超时。

魔改后的m2w在这里可以找到：[Github](https://github.com/Markkkkkkkk/m2w)，[Gitee](https://gitee.com/markk/m2w)；接下来我们介绍魔改后的m2w该如何使用。

**所有的m2w版本均依赖xmlrcp.php**，所以你的WordPress站点不要关闭其API（默认开放）。在WordPress 6.0时代，配合Wordfence，其实不需要太担心安全问题。建议站点有https的情况下再使用m2w，否则可能会造成帐号/密码泄露（如果博客仅有http，建议上https；可以看[这篇文章](https://hyly.net/categroy/article/code/wordpress/353/#header-id-22)）。

# 常规使用

## application_password 获取

首先获取`application_password`：

如果您使用 wordfence 之类的安全插件，请启用 WordPress 应用程序密码:

![img](https://image.hyly.net/i/2025/08/27/321ec1832fe1efcf00877b69ab4f6297-0.webp)

创建一个新的 REST API:

![img](https://image.hyly.net/i/2025/08/28/6c428375bc39e3d183bdacc44bb67314-0.webp)

安全地保管该API。如果有必要，可以重新生成或删除:

![img](https://image.hyly.net/i/2025/08/28/34a04329512a0c8278c2b8652527edbd-0.webp)

## 软件下载

在[Github](https://github.com/Markkkkkkkk/m2w)或[Gitee](https://gitee.com/markk/m2w)的发行版（Release）这里找到软件压缩包：

![image-20250828150957356](https://image.hyly.net/i/2025/08/28/cef5349c13219b9913b906fa0bee788c-0.webp)

![image-20250828151014532](https://image.hyly.net/i/2025/08/28/f8e0741d5e828cc7dba3b30a27378c06-0.webp)

下载下来然后解压，首先修改`config/user.json`文件：

![image-20250828151239260](https://image.hyly.net/i/2025/08/28/6e43e2196dbe8e6b2e8edf9ff7cc7e83-0.webp)

修改完成后用记事本打开`run_blog_and_git.bat`文件修改相应部分：

![image-20250828151632057](https://image.hyly.net/i/2025/08/28/c8ce3add01fc8c504d3a34d6780c4ecc-0.webp)

上面两个文件修改完之后保存，直接执行`run_blog_and_git.bat`就会自动上传文章到wordpress并把最新文章保存到git上去，这样原始文章样本就不会丢失了，而且可以方便查看文章修改记录。

大家在以后写Typora文章的时候也建议开头添加`YAML Front Matter`，就是类似这种：

![image-20250828155147169](https://image.hyly.net/i/2025/08/28/245e5eb47ddb186d02120cd956f6ebac-0.webp)

需要在文章的开头写，其它地方用这个语法是不管用的。具体是这样写的：

```
---
category: [博客建站]
tag: [服务器设置,SSH密钥登陆,Fail2ban,网站安全,wordfence,WPS Hide Login,CloudFlare]
postType: post
status: publish
---
```

1. category：文章/说说分类的名称。可以写多个，但建议只写一个，标签可以写多个。如果wordpress没有分类会创建分类，有则划分已有分类。
2. tag：文章/说说的标签，可以写多个。如果wordpress没有这个标签会创建标签，有则贴上已有标签。
3. postType：发布类型。post为文章，shuoshuo为发布说说。
4. status：文章状态。publish则运行m2w就会发布到wordpress上去，draft不会发布wordpress。（delete会删除wordpress上同名文章/说说，慎用，而且需要下文开启删除功能。）

# 源码下载

如果想看源码并再次进行魔改的小伙伴，可以直接下载源码进行自定义设置。推荐使用[Miniconda](https://gitee.com/link?target=https%3A%2F%2Fdocs.conda.io%2Fen%2Flatest%2Fminiconda.html)来管理Python版本和相关依赖，使用[Pycharm](https://www.jetbrains.com/pycharm/)工具进行代码修改，这是所需的依赖项：

```
# Python 版本要求
python_requires='>=3.7.6'

# 依赖项
install_requires=[
    "python-frontmatter>=1.0.0",
    "markdown>=3.3.6",
    "python-wordpress-xmlrpc>=2.3",
    "httpx>=0.24.0"
]
```

需要注意的是，在后来的版本中我觉得m2w能直接控制删除文章有点太危险了，而且这也不是高频操作，所以把通过设置`status：delete`状态来删除文章/说说的功能禁掉了。如果想拥有这个功能的小伙伴可以下载源码把这段注释解除就可以了，目录位置在`m2w/rest_api/update.py:90`这里：

![image-20250828154659658](https://image.hyly.net/i/2025/08/28/e88cef122909357441384bfdd6cf26d0-0.webp)

> **注意：**如果小伙伴还需要发布说说等，还需要添加说说接口函数，详细可以看[这篇文章](https://www.hyly.net/categroy/article/code/wordpress/380#header-id-6)。

# 小结

m2w的配置使用不是太难，使用过程中如有疑问或觉得想增加什么大家都喜欢的功能，请小伙伴们在下方留言，会考虑加上呼声最高的功能噢~
