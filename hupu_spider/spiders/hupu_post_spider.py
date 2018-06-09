# -*- coding: utf-8 -*-
import re
import time

import scrapy


class HupuPostSpider(scrapy.Spider):
    name = 'hupu_post'
    allowed_domains = ['bbs.hupu.com']

    # start_urls = ['http://bbs.hupu.com/bxj']

    def start_requests(self):
        for i in range(1, 17):
            # 有cookie的话可以设置cookie
            # scrapy.Request("http://www.xxxxxxx.com/user/login", meta={'cookiejar': 1}, headers=self.headers,
            #                callback=self.post_login)
            yield scrapy.Request('http://bbs.hupu.com/bxj-' + str(i))

    def parse(self, response):
        content_urls = []
        for li in response.xpath('//ul[@class="for-list"]/li'):
            # self.log(li.extract())
            title_href = li.xpath(".//a[@class='truetit']/@href").extract_first()
            url = "https://bbs.hupu.com" + title_href
            post_id = re.match('[^0-9]*(\d+)', title_href).group(1)
            title = li.xpath(".//a[@class='truetit']/text()").extract_first()
            author = li.xpath(".//a[@class='aulink']/text()").extract_first()
            post_time = li.xpath(".//a[@style='color:#808080;cursor: initial; ']/text()").extract_first()
            count_des = li.xpath(".//span[@class='ansour box']/text()").extract_first()
            reply_count = re.match('(\d+)[^0-9]*(\d+)', count_des).group(1)
            view_count = re.match('(\d+)[^0-9]*(\d+)', count_des).group(2)
            content_urls.append(url)

            yield {"id": post_id, "title": title, "url": url, "author": author, "post_time": post_time,
                   "view_count": view_count, "reply_count": reply_count}

        # 步行街帖子更新速度其实很慢，10分钟拉取一次就可以了
        time.sleep(10 * 60)
        yield self.response_retry(response)

    def post_content_parse(self, response):
        pass

    def response_retry(self, response):
        # request = response.request.copy()
        # original_request_url 为自定义设置的初始请求URL，在用IP代理时部分代理会修改URL
        request = response.request.replace(url=response.meta.get('original_request_url', response.url))
        # retry_times 为自定义重试次数
        retry_times = request.meta.get('retry_times', 0)
        request.dont_filter = True  # 这个一定要有，否则重试的URL会被过滤
        request.meta['retry_times'] = retry_times + 1

        return request


if __name__ == "__main__":
    print(re.match('[^0-9]*(\d+)', 'asdwesd/112812912.html').group(1))  # 在起始位置匹配
    print(re.match('(\d+)[^0-9]*(\d+)', '796 / 211403').group(2))  # 不在起始位置匹配
