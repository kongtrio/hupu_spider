# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem
import pymysql
import time
from hupu_spider import db_connection_pool as pool


class HupuSpiderPipeline(object):
    def process_item(self, item, spider):
        id = item.get("id")
        title = item.get("title")
        url = item.get("url")
        author = item.get("author")
        post_time = item.get("post_time")
        view_count = item.get("view_count")
        reply_count = item.get("reply_count")
        if id is None or title is None:
            raise DropItem("invalid item")

        self.insertOrUpdate(item)
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
        select_sql = "select id,view_count,reply_count from hupu_post where hupu_post_id=%s" % post_id

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
