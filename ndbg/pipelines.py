# -*- coding: utf-8 -*-
import pymongo
from os import mkdir

class NdbgPipeline(object):
    def __init__(self):
        self.client = pymongo.MongoClient('mongodb://localhost:27017')
        self.database = self.client['report']
        self.notes = self.database['notes']
        mkdir('reports/')

    def process_item(self, item, spider):
        self.notes.insert_one(item)
        # 保存到文件请解除这部分注释并删除其他内容
        path = 'reports/' + item['code'] + item['title'] + '.txt'
        with open(path, 'w') as file:
            file.write(item['content'])

    def close_spider(self, spider):
        self.client.close()