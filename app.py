from scrapers.pages.hackernews_scraper import HackernewsSpider
from large_models.llama3_processor import Llama3Processor
from large_models.prompters import hackernews_topics_prompter
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapers.pipelines import RedisWriterPipeline
from scrapy.utils.log import configure_logging

if __name__ == "__main__":

    custom_settings = {
        'LOG_LEVEL': 'ERROR',
        'ITEM_PIPELINES': {
            'scrapers.pipelines.RedisWriterPipeline': 300,
        }
    }

    process = CrawlerProcess({**get_project_settings(), **custom_settings})

    crawler = process.create_crawler(HackernewsSpider)
    process.crawl(HackernewsSpider)
    process.start()

    redisPipelineReader = RedisWriterPipeline()

    topics = ""
    for i in range(1000):
        topics += f"{(redisPipelineReader.get(f'item-{i}')['title'])};"

    processor = Llama3Processor()
    prompter = hackernews_topics_prompter.HackerNewsTopicsPrompter(topics)

    chain = prompter.generate_prompt() | processor.ollama
    
    print(chain.invoke({"input": "I am interested what happens in Google company"}))
    