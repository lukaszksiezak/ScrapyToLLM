from scrapers.pages.hackernews_scraper import HackernewsSpider

if __name__ == "__main__":
    from scrapy.crawler import CrawlerProcess
    process = CrawlerProcess()
    process.crawl(HackernewsSpider)
    process.start()