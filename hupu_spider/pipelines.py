# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem
from scrapy import Request
import pymysql
import time
from hupu_spider import db_connection_pool as pool
from scrapy.pipelines.images import ImagesPipeline


class HupuSpiderPipeline(object):
    def process_item(self, item, spider):
        item_type = item.get("type", 1)
        if item_type == 1:
            hupu_post_id = item.get("id")
            title = item.get("title")
            url = item.get("url")
            author = item.get("author")
            post_time = item.get("post_time")
            view_count = item.get("view_count")
            reply_count = item.get("reply_count")
            if hupu_post_id is None or title is None:
                raise DropItem("invalid item,type is %s" % item_type)

            self.insertOrUpdate(item)
            return item
        elif item_type == 2:
            hupu_post_id = item.get("id")
            old_post = self.getByPostId(hupu_post_id)
            # 如果设置过内容了，就不再设置内容了，浪费时间
            if old_post is not None and int.from_bytes(old_post[3], byteorder='big') == 1:
                return item
            content = item.get("content")
            post_time = item.get("post_time")
            if hupu_post_id is None or content is None or post_time is None:
                raise DropItem("invalid item,type is %s" % item_type)
            self.update_content(hupu_post_id, content, post_time)
            return item
        elif item_type == 3:
            content = item.get("content")
            hupu_reply_id = item.get("hupu_reply_id")
            author = item.get("author")
            hupu_post_id = item.get("hupu_post_id")
            reply_time = item.get("reply_time")
            like_count = item.get("like_count")
            if hupu_post_id is None or hupu_reply_id is None or reply_time is None:
                raise DropItem("invalid item,type is %s" % item_type)

            user_reply = self.get_reply_by_id(hupu_reply_id)
            if user_reply is None:
                self.insert_reply(item)
            elif user_reply[1] != int(like_count):
                self.update_reply(user_reply[0], like_count)
            return item
        else:
            return item

    def insertOrUpdate(self, item):
        try:
            post_time_str = item.get("post_time")
            post_time_sec = time.mktime(time.strptime(post_time_str, "%Y-%m-%d"))
            post_time_ms = int(post_time_sec) * 1000
        except:
            raise DropItem("error date")

        post_id = item.get("id")
        old_old = self.getByPostId(post_id)
        if old_old is None:
            insert_sql = "insert into hupu_post(hupu_post_id,title, author, url, post_time, view_count, reply_count, gmt_created)" \
                         " values (%s,'%s','%s','%s',%s,%s,%s,%s)" \
                         % (item.get("id"), item.get("title"), item.get("author"), item.get("url"), post_time_ms,
                            item.get("view_count"), item.get("reply_count"), int(time.time()) * 1000)

            with pool.get_db_connect() as db:
                db.cursor.execute(insert_sql)
                db.conn.commit()
        elif str(old_old[1]) == item.get("view_count") and str(old_old[2]) == item.get("reply_count"):
            print("hupuid:%s post nochange..." % old_old[0])
        else:
            print("update hupu......old viewcount=%s,now:%s" % (old_old[1], item.get("view_count")))
            self.update(old_old[0], item)

    def getByPostId(self, post_id):
        select_sql = "select id,view_count,reply_count,content_is_set from hupu_post where hupu_post_id=%s" % post_id

        with pool.get_db_connect() as db:
            db.cursor.execute(select_sql)
            results = db.cursor.fetchone()
            return results

    def update(self, id, item):
        update_sql = "update hupu_post set view_count=%s,reply_count=%s where id=%s" % (
            item.get("view_count"), item.get("reply_count"), id)

        with pool.get_db_connect() as db:
            db.cursor.execute(update_sql)
            db.conn.commit()

    def update_content(self, hupu_post_id, content, post_time_str):
        post_time_sec = time.mktime(time.strptime(post_time_str, "%Y-%m-%d %H:%M"))
        post_time_ms = int(post_time_sec) * 1000
        update_sql = "update hupu_post set post_time=%s,content='%s',content_is_set=1 where hupu_post_id=%s" % (
            post_time_ms, pymysql.escape_string(content), hupu_post_id)
        try:
            with pool.get_db_connect() as db:
                db.cursor.execute(update_sql)
                db.conn.commit()
        except:
            print("error content:" + content)

    def get_reply_by_id(self, reply_id):
        select_sql = "select id,like_count from hupu_post_reply where hupu_reply_id=%s" % reply_id

        with pool.get_db_connect() as db:
            db.cursor.execute(select_sql)
            results = db.cursor.fetchone()
            return results

    def update_reply(self, id, like_count):
        update_sql = "update hupu_post_reply set like_count=%s where id=%s" % (
            like_count, id)

        with pool.get_db_connect() as db:
            db.cursor.execute(update_sql)
            db.conn.commit()

    def insert_reply(self, item):
        reply_time_str = item.get("reply_time")
        reply_time_sec = time.mktime(time.strptime(reply_time_str, "%Y-%m-%d %H:%M"))
        reply_time_ms = int(reply_time_sec) * 1000

        insert_sql = "insert into hupu_post_reply(hupu_reply_id,author,hupu_post_id,reply_time,like_count,content,floor_num, gmt_created)" \
                     " values (%s,'%s',%s,%s,%s,'%s',%s,%s)" \
                     % (item.get("hupu_reply_id"), item.get("author"), item.get("hupu_post_id"), reply_time_ms,
                        item.get("like_count"), pymysql.escape_string(item.get("content")), item.get("floor_num"),
                        int(time.time()) * 1000)

        try:
            with pool.get_db_connect() as db:
                db.cursor.execute(insert_sql)
                db.conn.commit()
        except:
            print("error reply content:" + pymysql.escape_string(item.get("content")))


class HupuImgDownloadPipeline(ImagesPipeline):
    default_headers = {
        'accept': 'image/webp,image/*,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, sdch, br',
        'accept-language': 'zh-CN,zh;q=0.8,en;q=0.6',
        'cookie': 'bid=yQdC/AzTaCw',
        'referer': 'https://bbs.hupu.com/bxj',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
    }

    def get_media_requests(self, item, info):
        if item.get("image_urls") is not None:
            for image_url in item['image_urls']:
                self.default_headers['referer'] = image_url
                yield Request(image_url, headers=self.default_headers)
        # return []

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        item['image_paths'] = image_paths
        return item
