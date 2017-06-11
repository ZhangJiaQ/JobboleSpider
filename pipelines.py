# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import MySQLdb
import MySQLdb.cursors
from twisted.enterprise import adbapi


class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item

class MysqlTwistPipeline(object):
    def __init__(self,dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls,settings):

        dbparms = dict(
            host = settings["MYSQL_HOST"],
            passwd = settings["MYSQL_PASSWORD"],
            user = settings["MYSQL_USER"],
            db = settings["MYSQL_DBNAME"],
            charset = "utf8",
            cursorclass = MySQLdb.cursors.DictCursor,
            use_unicode = True
        )
        dbpool = adbapi.ConnectionPool("MySQLdb",**dbparms)

        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert,item)
        query.addErrback(self.handle_error,item,spider)

    def handle_error(self,failure,item,spider):
        # 处理异步插入的异常
        print(failure)

    def do_insert(self,cursor,item):
        # 执行具体的插入d
        insert_sql = """
                    insert into jobbole_article(title, url, create_time, fav_nums , url_object_id , front_image_url , parise_nums , comment_nums , tages, content)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
        cursor.execute(insert_sql, (item["title"], item["url"], item["create_time"], item["fav_nums"], item["url_object_id"], item["front_image_url"], item["parise_nums"], item["comment_nums"], item["tages"],item["content"]))