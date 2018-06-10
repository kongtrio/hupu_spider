# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class HupuPost(scrapy.Item):
    # define the fields for your item here like:
    id = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    author = scrapy.Field()
    post_time = scrapy.Field()
    view_count = scrapy.Field()
    reply_count = scrapy.Field()
    content = scrapy.Field()
    type = scrapy.Field()


class HupuPostReply(scrapy.Item):
    hupu_reply_id = scrapy.Field()
    author = scrapy.Field()
    hupu_post_id = scrapy.Field()
    reply_time = scrapy.Field()
    like_count = scrapy.Field()
    floor_num = scrapy.Field()
    content = scrapy.Field()


class HupuImageItem(scrapy.Item):
    image_urls = scrapy.Field()  # 图片的链接
    images = scrapy.Field()
    image_paths = scrapy.Field()
