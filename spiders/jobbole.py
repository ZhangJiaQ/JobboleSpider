# -*- coding: utf-8 -*-
import scrapy
import re

class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/102337/']

    def parse(self, response):
        title = response.xpath('//*[@id="post-102337"]/div[1]/h1/text()').extract()[0]

        create_date = response.xpath('//*[@id="post-102337"]/div[2]/p/text()').extract()[0].strip().replace("·","").strip()

        praise_nums = response.xpath('//*[@id="102337votetotal"]/text()').extract()[0]


        fav_nums = response.xpath('//*[@id="post-102337"]/div[3]/div[3]/span[2]/text()').extract()[0]
        fav_match = re.match(r'.*(\d+).*',fav_nums)
        if fav_match is not None:
            fav_nums = fav_match.group(1)

        comment_nums = response.xpath('//*[@id="post-102337"]/div[3]/div[3]/a/span/text()').extract()[0]
        comment_match = re.match(r'.*(\d+).*',comment_nums)
        if comment_match is not None:
            comment_nums = comment_match.group(1)

        content = response.xpath('//div[@class="entry"]').extract()[0]

        tag_list = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/a/text()').extract()
        tag_list = [element for element in tag_list if not element.strip().endswith("评论")]
        tags = ",".join(tag_list)


        pass
