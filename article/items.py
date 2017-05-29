# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst

import datetime
def convertDatetime(value):
    try:
        create_time = datetime.datetime.strptime(value, "%Y/%m/%d").date()
    except Exception as e:
        create_time = datetime.datetime.now().date()
    return create_time

def return_value():
    return

from scrapy.loader.processors import MapCompose, TakeFirst
class ArticleItemLoader(ItemLoader):
    #自定义itemloader
    default_output_processor = TakeFirst()


class JobArticleItem(scrapy.Item):
    title = scrapy.Field(
        input_processor=MapCompose(lambda x : x+"jobbole"),
    ) #文章标题
    url = scrapy.Field() #文章链接
    create_time = scrapy.Field(
        input_processor=MapCompose(convertDatetime),
    )  #文章发布时间
    favor_count = scrapy.Field()  # 文章点赞次数
    collect_count = scrapy.Field() # 文章收藏次数
    front_image_url = scrapy.Field() # 文章列表中的图片url
    front_image_path = scrapy.Field() # 图片本地的保存路径
    tags = scrapy.Field() #文章的标签
    url_md5 = scrapy.Field() #固定url长度