import scrapy

class ScrapeNYTMItem(scrapy.Item):
    emails = scrapy.Field()
    domain = scrapy.Field()
    urls = scrapy.Field()
    num_pages = scrapy.Field()
    num_parsed = scrapy.Field()
