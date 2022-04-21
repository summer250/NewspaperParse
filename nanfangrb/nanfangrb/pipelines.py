# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pymongo
from scrapy.utils.project import get_project_settings


class NanfangrbPipeline_DB:

    def __init__(self):
        settings = get_project_settings()
        host = settings["MONGODB_HOST"]
        port = settings["MONGODB_PORT"]
        dbname = settings["MONGODB_DBNAME"]
        sheetname = settings["MONGODB_DOCNAME"]

        # 创建MONGODB数据库链接
        client = pymongo.MongoClient(host=host, port=port)
        # 指定数据库
        mydb = client[dbname]
        # 存放数据的数据库表名
        self.sheet = mydb[sheetname]

    def process_item(self, item, spider):
        data = dict(item)
        self.sheet.insert_one(data)
        return item
