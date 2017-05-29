# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import Request
from urllib import parse

from article.items import JobArticleItem, ArticleItemLoader
from article.utils.common import get_md5
from scrapy.loader import ItemLoader

class JobboleSpider(scrapy.Spider):
    name = "jobbole"
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):

        # 解析获取当前页面中的所有文章url,并传递给parse_details方法做具体解析
        post_node = response.css("#archive .floated-thumb .post-thumb a")
        for node in post_node:
            image_url = node.css("img::attr(src)").extract_first("")
            title_url = node.css("::attr(href)").extract_first("")
            yield Request(url=parse.urljoin(response.url, title_url), meta={"front_image_url": image_url},callback=self.parse_details)

        next_url = response.css(".next.page-numbers::attr(href)").extract_first()
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)


    def parse_details(self, response):
        # 提取而文章详情页信息逻辑
        title = response.xpath('//div[@class="entry-header"]/h1/text()').extract()[0]
        create_time = response.css("p.entry-meta-hide-on-mobile::text").extract()[0].strip().replace("·", "").strip()

        favor_count = int(response.xpath("//span[contains(@class, 'vote-post-up')]/h10/text()").extract()[0])
        collect_count = response.css(".bookmark-btn::text").extract()[0]
        collect_match = re.match(".*?(\d+).*", collect_count)
        if collect_match:
            collect_count = int(collect_match.group(1))
        else:
            collect_count = 0

        front_image_url = response.meta.get("front_image_url", "")

        # jobArticleItem = JobArticleItem()
        # jobArticleItem["title"] = title
        # jobArticleItem["url"] = response.url
        # jobArticleItem["url_md5"] = get_md5(response.url)
        # jobArticleItem["create_time"] = create_time
        # jobArticleItem["favor_count"] = favor_count
        # jobArticleItem["collect_count"] = collect_count
        # jobArticleItem["front_image_url"] = [front_image_url]

        itemloader = ArticleItemLoader(item=JobArticleItem(), response=response)
        itemloader.add_xpath('title', '//div[@class="entry-header"]/h1/text()')
        itemloader.add_value('url', response.url)
        itemloader.add_value('url_md5', get_md5(response.url))
        itemloader.add_css('create_time', 'p.entry-meta-hide-on-mobile::text')
        itemloader.add_value('favor_count', favor_count)
        itemloader.add_value('collect_count', collect_count)
        itemloader.add_value('front_image_url', [front_image_url])

        article_item = itemloader.load_item()
        yield article_item