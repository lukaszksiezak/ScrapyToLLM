import json
import redis
from itemadapter import ItemAdapter

class RedisWriterPipeline:
    def __init__(self) -> None:
        self.idx = 0

    def open_spider(self, spider):
        self.redis_client = redis.Redis(host='localhost', port=6379, username="default", password="mypassword", decode_responses=True)

    def process_item(self, item, spider):
        self.redis_client.hset(f'item-{self.idx}', mapping={
            'title': item['title'],
            'url': item['url']
        })
        self.idx += 1
