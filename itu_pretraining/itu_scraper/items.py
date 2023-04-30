import scrapy

class TextItem(scrapy.Item):
    url = scrapy.Field()
    text = scrapy.Field()
