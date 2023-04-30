import scrapy
from scrapy.linkextractors import LinkExtractor
from myproject.items import TextItem
from urllib.parse import urlparse
import re

def should_skip_domain(url, skip_domains):
    domain = urlparse(url).netloc
    return any(skip_domain in domain for skip_domain in skip_domains)

class MySpider(scrapy.Spider):
    name = 'my_spider'
    allowed_domains = ['itu.edu.pk']
    start_urls = ['https://itu.edu.pk']
    skip_domains = ['library.itu.edu.pk']

    def parse(self, response):
        if should_skip_domain(response.url, self.skip_domains):
            return

        item = TextItem()
        item['url'] = response.url

        # Select only text nodes, ignoring script and style elements
        text_nodes = response.xpath('//body//*[not(self::script or self::style)]/text()')
        raw_text = ' '.join(text_nodes.extract()).strip()

        # Replace newline, tab, and carriage return characters with spaces
        cleaned_text = re.sub(r'[\n\t\r]+', ' ', raw_text)

        # Remove the specific text pattern
        pattern_to_remove = r'HOME\s+ABOUT\s+CAREERS\s+CONTACT\s+©\s+\d+\s+Information\s+Technology\s+University\s+of\s+the\s+Punjab'
        text_without_pattern = re.sub(pattern_to_remove, '', cleaned_text)

        # Replace multiple consecutive spaces with a single space
        final_text = re.sub(r'\s{2,}', ' ', text_without_pattern)

        item['text'] = final_text

        yield item

        link_extractor = LinkExtractor(allow_domains=self.allowed_domains)
        for link in link_extractor.extract_links(response):
            if not should_skip_domain(link.url, self.skip_domains):
                yield scrapy.Request(link.url, callback=self.parse)


