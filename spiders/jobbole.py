# -*- coding: utf-8 -*-
import datetime
from urllib import parse

import scrapy
import re
from scrapy.http import Request
from ArticleSpider.items import JobboleArticleItem
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

        article_item = JobboleArticleItem()

        front_image_url = response.meta.get("front_image_url", "")# feng mian tu

        title = response.css('#wrapper .entry-header h1::text').extract()[0]

        create_date = response.css('.grid-8 .entry-meta-hide-on-mobile ::text').extract()[0].strip().replace("·","").strip()

        parise_nums = int(response.css(".vote-post-up h10::text").extract()[0])

        fav_nums = response.css(".bookmark-btn::text").extract()[0]
        match_re = re.match(".*?(\d+).*", fav_nums)
        if match_re:
            fav_nums = int(match_re.group(1))
        else:
            fav_nums = 0

        comment_nums = response.css("a[href='#article-comment'] span::text").extract()[0]
        match_re = re.match(".*?(\d+).*", comment_nums)
        if match_re:
            comment_nums = int(match_re.group(1))
        else:
            comment_nums = 0

        content = response.xpath('//div[@class="entry"]').extract()[0]

        tag_list = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/a/text()').extract()
        tag_list = [element for element in tag_list if not element.strip().endswith("评论")]
        tags = ",".join(tag_list)

        """
        front_image_path = scrapy.Field()
        """
        article_item["title"] = title
        try:
            create_date = datetime.datetime.strptime(create_date, "%Y:%m:%d").date()
        except Exception as e:
            create_date = datetime.datetime.now().date()


        article_item["create_time"] = create_date
        article_item["parise_nums"] = parise_nums
        article_item["comment_nums"] = comment_nums
        article_item["fav_nums"] = fav_nums
        article_item["tages"] = tags
        article_item["content"] = content
        article_item["url"] = response.url
        article_item["url_object_id"] = get_md5(response.url)
        article_item["front_image_url"] = front_image_url


        yield article_item
