# hupu_spider
用scrapy框架写了一个爬取虎扑步行街帖子的爬虫
步行街地址：
https://bbs.hupu.com/bxj

### 目前完成功能
1. 爬取帖子，获取作者，发帖时间，帖子浏览数，回帖数等信息存到数据库中
2. 爬取帖子内容，获取回帖的数据并插入到数据库中
3. 下载帖子内容中的图片

### 待完善
1. 随机切换user-agent.目前没有设置user-agent，虎扑估计没怎么做反爬，所以目前没遇到什么问题。但是为了避免将来爬虫突然失效，还是做一下user-agent设置比较稳妥
2. 添加代理，防止ip被封

### 安装步骤
需要安装的软件
- python3
- mysql

需要安装的python库:
- scrapy
- pillow(用于下载图片，如果不用下载图片可以不用这个库)
- DBUtils
- pymysql
-
```
pip install scrapy
pip install pillo
pip install DBUtils
pip install pymysql
```

当需要的软件和库都安装好后，进行以下步骤
1. 进入mysql环境，创建数据库。`create database hupu`。当然，数据库不叫虎扑也可以，到时记得改项目中的配置文件
2. 执行该项目中的 `mysql_db/hupu_post.sql` 创建相关的表。
3. 修改`db_config.py`中的数据库配置。包括用户密码，数据库等。
4. 如果要下载图片，需要修改`settings.py`中的`IMAGES_STORE`变量，同时将`ITEM_PIPELINES`变量的`HupuImgDownloadPipeline`那行的注释去掉。项目默认是不下载图片的。
5. 执行`./run.sh`运行程序，window环境下直接在hupu_spider目录下执行 `scrapy crawl hupu_post` 也是一样的。

### 相关问题
##### 1. 执行发现报`ModuleNotFoundError: No module named '_sqlite3'`错误
说明服务器可能没安装sqlite3.可以执行`yum install sqlite*`来安装。如果你的服务器没有yum，或者yum安装sqlite失败(yum安装失败建议更换一下yum源再尝试)。
那就去下载一下sqlite的包，然后自己编译安装了。具体安装教程可以去网上找，有很多。
`安装完sqlite的包后需要重新编译安装一下python才可以生效。`
安装编译python教程：<https://blog.csdn.net/u013332124/article/details/80643371>