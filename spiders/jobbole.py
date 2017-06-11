# -*- coding: utf-8 -*-
import datetime
from urllib import parse

import scrapy
import re
from scrapy.http import Request
from scrapy.loader import ItemLoader

from ArticleSpider.items import JobboleArticleItem,ArticleItemLoader
from ArticleSpider.utills.common import get_md5

class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        """
        1. 获取文章列表页中的文章url并交给scrapy下载后并进行解析
        2. 获取下一页的url并交给scrapy进行下载， 下载完成后交给parse
        """
        # 解析列表页中的所有文章url并交给scrapy下载后并进行解析
        post_nodes = response.css('#archive .floated-thumb .post-thumb a')
        for post_node in post_nodes:
            image_url = post_node.css("img::attr(src)").extract_first("")
            post_url = post_node.css("::attr(href)").extract_first("")
            yield Request(url=parse.urljoin(response.url, post_url), meta={"front_image_url": image_url},callback=self.content_parse)

        # 提取下一页并交给scrapy进行下载
        next_url = response.css('.navigation .next ::attr(href)').extract_first("")
        if next_url:
            yield Request(url=parse.urljoin(response.url,next_url),callback=self.parse)


    def content_parse(self , response):

        front_image_url = response.meta.get("front_image_url", "")# feng mian tu

        # 通过item loader加载item
        item_loader = ArticleItemLoader(item=JobboleArticleItem(),response=response)
        item_loader.add_css("title",'#wrapper .entry-header h1::text')
        item_loader.add_css("create_time",".grid-8 .entry-meta-hide-on-mobile ::text")
        item_loader.add_css("parise_nums",".vote-post-up h10::text")
        item_loader.add_css("comment_nums","a[href='#article-comment'] span::text")
        item_loader.add_css("fav_nums",".bookmark-btn::text")
        item_loader.add_xpath("tages",'//p[@class="entry-meta-hide-on-mobile"]/a/text()')
        item_loader.add_xpath("content",'//div[@class="entry"]')
        item_loader.add_value("url",response.url)
        item_loader.add_value("url_object_id",get_md5(response.url))
        item_loader.add_value("front_image_url",front_image_url)

        article_item = item_loader.load_item()

        yield article_item