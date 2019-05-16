# -*- coding: utf-8 -*-
import re
import time

import scrapy
import logging


class HupuPostSpider(scrapy.Spider):
    name = 'hupu_post'
    allowed_domains = ['bbs.hupu.com']
    page_compile = re.compile("^.*pageCount:(\d+)", re.S)

    def __init__(self, category=None, *args, **kwargs):
        super(HupuPostSpider, self).__init__(*args, **kwargs)
        self.max_page = kwargs.get("max_page", 5)
    '''
    爬取起始页面函数 url命名规则为http://bbs.hupu.com/dota2-x
    '''
    def start_requests(self):

        for i in range(1, int(self.max_page) + 1):
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
            post_id = self.get_post_id(title_href)
            title = li.xpath(".//a[@class='truetit']/text()").extract_first()
            author = li.xpath(".//a[@class='aulink']/text()").extract_first()
            post_time = li.xpath(".//a[@style='color:#808080;cursor: initial; ']/text()").extract_first()
            count_des = li.xpath(".//span[@class='ansour box']/text()").extract_first()
            reply_count = re.match('(\d+)[^0-9]*(\d+)', count_des).group(1)
            view_count = re.match('(\d+)[^0-9]*(\d+)', count_des).group(2)
            content_urls.append(url)

            yield {"id": post_id, "title": title, "url": url, "author": author, "post_time": post_time,
                   "view_count": view_count, "reply_count": reply_count}

        for content_url in content_urls:
            yield scrapy.Request(content_url, self.post_content_parse, dont_filter=True)

        # dota2帖子更新速度其实很慢，10分钟拉取一次就可以了
        # time.sleep(10 * 60)
        # yield self.response_retry(response)

    #处理帖子首页函数

    def post_content_parse(self, response):
        # 获取一共有几页
        page_match = self.page_compile.match(response.text)
        total_pages = 1
        if page_match is not None:
            total_pages = int(page_match.group(1))

        content = response.xpath("//div[@class='quote-content']").extract_first()

        post_detailt_time = response.xpath("//div[@class='floor-show']//span[@class='stime']/text()").extract_first()
        post_id = self.get_post_id(response.url)
        yield {"type": 2, "content": content, "post_time": post_detailt_time, "id": post_id}


        #使用xpath匹配信息


        for reply in response.xpath("//div[@class='floor']"):
            if reply.xpath("@id") is None:
                continue
            hupu_reply_id = reply.xpath("@id").extract_first()
            floor_num = reply.xpath(".//a[@class='floornum']/@id").extract_first()
            if hupu_reply_id == "tpc" or floor_num is None:
                continue
            author = reply.xpath(".//div[@class='author']//a[@class='u']/text()").extract_first()
            reply_time = reply.xpath(".//div[@class='author']//span[@class='stime']/text()").extract_first()
            like_count = reply.xpath(
                ".//div[@class='author']//span[@class='ilike_icon_list']//span[@class='stime']/text()").extract_first()
            contents = reply.xpath(".//tbody//td//text()").extract()
            content = ""

            '''
            使用正则表达式筛选内容
            1.去掉空字符
            2.去掉引用
            3.去掉发自**
            4.去掉修改
            '''
            for con in contents:
                if con == "":
                    continue
                quotematch = re.match("^引用", con)
                if quotematch is not None:
                    continue

                sendmatch = re.match("^发自", con)
                if sendmatch is not None:
                    continue

                modifiedmatch = re.match("修改", con)
                if modifiedmatch is not None:
                    continue
                content += con.strip()


            #返回爬取内容

            yield {"type": 3, "content": content, "hupu_reply_id": hupu_reply_id, "author": author,
                   "hupu_post_id": post_id, "reply_time": reply_time, "like_count": like_count, "floor_num": floor_num}


        #如果帖子有多页，则调用post_content_page_parse函数处理后面的页

        if total_pages > 1:
            for page in range(2, total_pages + 1):
                url = "https://bbs.hupu.com/%s-%s.html" % (post_id, page)
                scrapy.Request(url, self.post_content_page_parse, dont_filter=True)

        image_urls = response.xpath("//tbody//img/@src").extract()
        if len(image_urls) > 0:
            yield {"type": 999, "image_urls": image_urls}
    '''
    处理帖子后几页函数，大致内容同上
    '''
    def post_content_page_parse(self, response):
        post_id = self.get_post_id(response.url)
        for reply in response.xpath("//div[@class='floor']"):
            if reply.xpath("@id") is None:
                continue
            hupu_reply_id = reply.xpath("@id").extract_first()
            if hupu_reply_id == "tpc":
                continue
            author = reply.xpath(".//div[@class='author']//a[@class='u']/text()").extract_first()
            reply_time = reply.xpath(".//div[@class='author']//span[@class='stime']/text()").extract_first()
            like_count = reply.xpath(
                ".//div[@class='author']//span[@class='ilike_icon_list']//span[@class='stime']/text()").extract_first()
            #content = reply.xpath(".//tbody").extract_first().strip()
            contents = reply.xpath(".//tbody//td//text()").extract()
            content = ""
            for con in contents:
                quotematch = re.match("^引用", con)
                if quotematch is not None:
                    continue
                if con == "":
                    continue
                sendmatch = re.match("^发自", con)
                if sendmatch is not None:
                    continue
                modifiedmatch = re.match("修改", con)
                if modifiedmatch is not None:
                    continue
                content += con.strip()

            yield {"type": 3, "content": content, "hupu_reply_id": hupu_reply_id, "author": author,
                   "hupu_post_id": post_id, "reply_time": reply_time, "like_count": like_count}

    def response_retry(self, response):
        # request = response.request.copy()
        # original_request_url 为自定义设置的初始请求URL，在用IP代理时部分代理会修改URL
        request = response.request.replace(url=response.meta.get('original_request_url', response.url))
        # retry_times 为自定义重试次数
        retry_times = request.meta.get('retry_times', 0)
        request.dont_filter = True  # 这个一定要有，否则重试的URL会被过滤
        request.meta['retry_times'] = retry_times + 1

        return request

    @staticmethod
    def get_post_id(url):
        # 后面可以做个编译
        # re_compiler = re.compile(r'^(\d{3})-(\d{3,8})$')
        # re.match('[^0-9]*(\d+)', url).group(1)
        return re.match('[^0-9]*(\d+)', url).group(1)


if __name__ == "__main__":
    content = '''window.location.href='https://bbs.hupu.com/'+url''\n
    hello
            }
          }
        }
       break;
     default:
       break;
   }

  }
},{
  pageCount:10,//总页码,默认10
  current:1,//当前页码
  name:detail_url+'-',//标记
  hname:detail_url,
  showNear:pageNum,//显示当前页码前多少页和后多少页，默认2
  pageSwap:true,
  align:'right',
  is_read:1,
  showSumNum:false,//是否显示总页码
  maxpage:10
  
    '''
    print(re.match('[^0-9]*(\d+)', 'https://bbs.hupu.com/22537299-2.html').group(1))  # 在起始位置匹配
    print(re.match('^.*pageCount:(\d+)', content, re.S).group(1))  # 不在起始位置匹配
    for i in range(1, 2):
        print("helo")
