# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import logging


class ScrapyWikipediaPipeline:
    def process_item(self, item, spider):
        return item

class FailurePipeline:
    def __init__(self):
        self.failed_urls = []

    @classmethod
    def from_crawler(cls, crawler):
        return cls()

    def process_exception(self, request, exception, spider):
        self.failed_urls.append(request.url)
        logging.error(f"Failed to scrape: {request.url}")

    def close_spider(self, spider):
        with open("failed_urls.txt", "w") as file:
            for url in self.failed_urls:
                file.write(url + "\n")
