from scrapy.spiders import CrawlSpider
import scrapy

class ScrapedItem(scrapy.Item):
    """
    Abstract class for all scraped items
    """
    pass

class Scraper(CrawlSpider):
    """
    Abstract class for all scrapers
    """
    name = None
    allowed_domains = []
    start_urls = []

    def parse_item(self, response):
        """
        Abstract method to be implemented by all scrapers
        """
        raise NotImplementedError("Subclasses must implement this method")
