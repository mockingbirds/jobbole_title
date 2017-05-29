# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html



class ArticlePipeline(object):
    def process_item(self, item, spider):
        return item

import codecs
import json

class JsonwithEncodingPipeline(object):
    def __init__(self):
        self.file = codecs.open('article.json', 'w', 'utf-8')

    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n" #将item转换成字符串
        self.file.write(lines) #将lines内容写入到file文件中
        return item

    def spider_close(self, spider):
        self.file.close() #当当前spider执行完成之后，会回调spider_close方法，在这里关闭file文件

from scrapy.exporters import JsonItemExporter

class JsonItemExporterPipeline(object):
    # 使用JsonItemExporter将item保存为json文件
    def __init__(self):
        self.file = open('articleexporter.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

    def spider_close(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

import MySQLdb

class MysqlItemPipeline(object):
    def __init__(self):
        self.conn= MySQLdb.connect(
                        host='localhost',
                        port=3306,
                        user='root',
                        passwd='root',
                        db='articlespider',
                        charset='utf8',
                        use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """
            insert into article_table (title, create_time, favor_count, collect_count, front_image_url, url)
                    values(%s, %s, %s, %s, %s, %s)dd
        """
        self.cursor.execute(insert_sql, (item['title'], item['create_time'], item['favor_count'], item['collect_count'],
                                         item['front_image_url'], item['url']))
        self.conn.commit()
        return item


from twisted.enterprise import adbapi
import MySQLdb.cursors
import MySQLdb

class MyTwistedPipeline(object):
    def __init__(self, dbpool):
        # 在执行完from_settings之后,将dbpool初始化
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparams = dict(
            host=settings["MYSQL_HOST"],
            port=settings["MYSQL_PORT"],
            user=settings["MYSQL_USER"],
            passwd=settings["MYSQL_PWD"],
            db=settings["MYSQL_DB"],
            charset=settings["MYSQL_CHARSET"],
            use_unicode=settings["MYSQL_USER_UNICODE"],
            cursorclass=MySQLdb.cursors.DictCursor,
        )
        # 这里通过adbapi构造一个dbpool，并传入MyTwistedPipeline的构造方法
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparams)
        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted异步插入数据到mysql
        query = self.dbpool.runInteraction(self.insert_data, item)
        query.addErrback(self.handle_error)
        return item

    def handle_error(self,failure):
        # 处理异步插入异常
        print(failure)

    def insert_data(self, cursor, item):
        # 执行插入操作
        insert_sql = """
                    insert into article_table (title, create_time, favor_count, collect_count, front_image_url, url)
                            values(%s, %s, %s, %s, %s, %s)
                """
        cursor.execute(insert_sql, (item['title'], item['create_time'], item['favor_count'], item['collect_count'],
                                         item['front_image_url'], item['url']))
