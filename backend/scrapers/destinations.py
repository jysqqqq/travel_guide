import scrapy


class DestinationsSpider(scrapy.Spider):
    name = "destinations"
    allowed_domains = ["mafengwo.cn"]
    start_urls = ["https://mafengwo.cn"]

    def parse(self, response):
        pass
