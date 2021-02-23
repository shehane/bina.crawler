# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json
import codecs
from itemadapter import ItemAdapter
from scrapy.exporters import JsonItemExporter


class BinaPipeline:
    def process_item(self, item, spider):
        return item
# class FlatPipeline:
#     def process_item(self, item, spider):
#         return item

# ideya pravilnaya, oba pipelina nujni, pravilnoe napravlenie est :)
# for now let's try something else then you can go back to pipelines
class JsonWriterPipeline(BinaPipeline):

    def open_spider(self, spider):
        self.file = open('listings.json', 'w')
        self.items_list = []
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        # self.exporter.start_exporting()

    def close_spider(self, spider):
        self.file.write("[\n")

        for i in self.items_list:
            self.file.write(json.dumps(ItemAdapter(i).asdict()) + "\n")

        self.file.write("\n]")

        self.file.close()

    def process_item(self, item, spider):
        if spider.name == 'bina.az':
            self.items_list.append(item)
            return item

class FetchBina(BinaPipeline):
    # def open_spider(self, spider):
    #     self.file = codecs.open('flats.json', 'w',encoding='utf-8')
    #     self.flats_list = []
    #
    # def close_spider(self, spider):
    #     self.file.write("["+'\n')
    #
    #     for i in self.flats_list:
    #         self.file.write(json.dumps(ItemAdapter(i).asdict()) + "\n")
    #
    #     self.file.write("\n"+']')
    #
    #     self.file.close()

    def process_item(self, item, spider):
    #   self.flats_list.append(item)
        return item

