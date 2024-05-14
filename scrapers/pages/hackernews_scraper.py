from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from scrapy.spiders import Rule
from scrapers.scraper import Scraper, ScrapedItem
import scrapy


class ArticleItem(ScrapedItem):
    title = scrapy.Field()
    url = scrapy.Field()

class HackernewsSpider(Scraper):
    name = 'pythonhackernews'
    allowed_hosts = ['news.ycombinator.com']
    start_urls = ['https://news.ycombinator.com/news?p=1']

    rules = (Rule(LinkExtractor(allow=r'news\?p=[0-2]'), #[0-9]'),
                  callback="parse_item",
                  follow=True),)

    def parse_item(self, response):

        items = []
        selector = Selector(response)
        links = selector.xpath('//td[@class="title"]').xpath('//span[@class="titleline"]')

        for link in links:
            title = link.xpath("a/text()").extract()
            url = link.xpath("a/@href").extract()

            if title and url:
                title, url = title[0], url[0]

                item = ArticleItem()
                item['title'] = title
                item['url'] = url

                items.append(item)
                yield item

    def closed(self, reason):
        print(f"Spider finished scraping. Reason: {reason}")
