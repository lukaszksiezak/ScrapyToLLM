
https://lukaszksiezak.github.io/ScrapyToLLM/

# Hack the Newsfeed with LLM AI in 15 mins

In this article, I delve into a simple (yet powerful) project that leverages the power of LLMs to create a personalized tech-news recommendation system. The application scrapes Hacker News and suggests articles to users, based on their preferences. Utilizing the Ollama and LangChain libraries, the system employs the LLAMA3 model for natural language understanding and Redis as an in-memory storage solution for managing scraped data.

In this article I’ll guide you through the process, highlighting how LLMs can simplify complex tasks and make information retrieval as easy as asking a friend. In my opinion it’s also great starter project for anyone interested in experimenting with LLMs locally and witnessing their use in real-case scenario.

# Key Components of the Project
Scraping: The application scrapes articles from Hacker News, ensuring an up-to-date repository of the latest tech news, using scrapy (https://scrapy.org/) library.
LLMs: The LLAMA3 (https://llama.meta.com/llama3/) model processes user inputs and the scraped data to provide relevant article suggestions. LangChain(https://python.langchain.com/) used to integrate LLM in the application.
Data Flow: Redis (https://redis.io/) is employed as a local in-memory storage to handle the high volume of scraped data efficiently.
Prompting User Preferences: Users can express their preferences through prompts, allowing the system to tailor recommendations specifically to their interests.
The project is written in Python, leveraging its ecosystem and ease of integration with various libraries. Redis was served as a Docker container.

# Prerequisities
The project is structured into several key components that work together to scrape Hacker News, store the scraped data in Redis, and use LLAMA3 to generate personalized article recommendations based on user preferences. Below is a detailed breakdown of the project code, split into sections with descriptions for interesting parts.

# Setting up environment

*I built this application on Windows 10 machine and all the commands presented below were tested in that environment.

### Redis:
Redis is a high-performance in-memory data structure store, commonly used as a database, cache, and message broker. In the context of our personalized tech-news recommendation system, Redis serves as an intermediate local storage solution between the scraping system (using Scrapy) and the Large Language Model (LLM) processing component.

Let’s pull docker image and start the container (Docker Desktop must be installed and running):

```
> docker pull redis/redis-stack
> docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 -e redis/redis-stack:latest
```

If all goes well, you should be able to access redis-stack (web interface) on https://localhost:8001

### LLAMA3–7b model using Ollama

First, you need to download and install Ollama client: https://ollama.com/download. Once done, pull LLAMA3–7b model:

```
> ollama pull llama3:8b
```

It’s a content for a separate article about differences between models and number of parameters, for reference I recommend Meta’s blog: https://ai.meta.com/blog/meta-llama-3/

Once the model is ready, you should see it in a list:

```
> ollama list
NAME            ID              SIZE    MODIFIED   
llama3:latest   a6990ed6be41    4.7 GB  6 days ago
```

## The code

The project is structured into several key components that work together to scrape Hacker News, store the scraped data in Redis, and use a Large Language Model (LLM) to generate personalized article recommendations based on user preferences. Below is a detailed breakdown of the project code, split into sections with descriptions for interesting parts

### Main

This is the main script that orchestrates the entire process of scraping data, storing it in Redis, and generating recommendations using an LLM.

```
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
    
    print(chain.invoke({"input": "I'd like to learn something about quantum mechanics"}))
```

Before jumping into details of each component, let’s walk through the main bits of code.

- In the beginning we’re setting up Scrapy, including configuring the Redis pipeline.
- We start the crawler for the HackernewsSpider.
- Scraped data is read from Redis to prepare it for the LLM.
- HackerNewsTopicsPrompter is preparing the prompt structure which is then invoked as a chain (so we leverge from LLAMA3–7b + embeddings (news topics)) against user prompt.

The scraper

```
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

    rules = (Rule(LinkExtractor(allow=r'news\?p=[0-9]'),
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
```

- For scraping we use CrawlSpider with rules to follow pagination links and extract data.
- Selectors extracts article titles and URLs using XPath expressions.
- Produced ArticleItem instances are yelded to be processed by the pipeline.

## The prompter

```
from langchain_core.prompts import ChatPromptTemplate
from .prompter import Prompter

class HackerNewsTopicsPrompter(Prompter):

    _available_topics = None

    def __init__(self, available_topics):
        self._available_topics = available_topics

    def generate_prompt(self):
        return ChatPromptTemplate.from_messages([
            ("system", f"You are an AI assistant which supports a user in choosing the most interesting topic for him. 
                         Here's a list of topics he can access 
                         (comma separated): {self._available_topics}"),
            ("user", "{input}")
        ])
```
That’s a standard usage of a langchain. We use a system definition prompt, in order to instruct the model how to interpret user’s input. The prompt is enriched with list of topics scraped from the HackerNews page.

Yup, that’s prompt engineering (we should probably get used to it).

## Running the app
Application can be executed in python’s virtual environment, after installing requirements.

```
python -m venv .venv
.venv\Scripts\Activate.bat
pip install -r requirements.txt
python app.py
```

For given prompt (as defined in app.py), following topics recommendations have been given:

```
Quantum mechanics is a vast and complex topic. 
But if you're new to the subject, it might be helpful to start with some 
introductory resources. Here are a few suggestions:

1. "QED: The Strange Theory of Light" by Richard P. Feynman - This classic book provides an accessible introduction to quantum electrodynamics.
2. "The Quantum Universe" by Brian Cox and Jeff Forshaw - This text explores the basics of quantum mechanics in an engaging and easy-to-understand manner.
3. "Quantum: Einstein, Bohr, and the Great Debate About the Nature of Reality" by Manjit Kumar - This book delves into the history and development of quantum mechanics.

These resources should provide a solid foundation for exploring quantum mechanics further. 
Would you like me to suggest more topics from 2009 or help you find additional resources on this topic?
```
Which is kind of surprising output, since non of given resources have shown up recently on hackernews. That reveals a big challenge we’ll be facing when working with LLMs — we don’t really know what the model was trained on. Therefore testing is more important than ever to assure applications’ determinism (have you heard of Air Canada exposing their AI Assistant to the customers? https://hackaday.com/2024/02/28/air-canadas-chatbot-why-rag-is-better-than-an-llm-for-facts/)

Let’s try modyfing prompter and executing the app again:

```
def generate_prompt(self):
        return ChatPromptTemplate.from_messages([
            ("system", f"You are an AI assistant which supports a user in 
                         choosing the most interesting topic for him. 
                         Here's a list of topics he can access 
                         (comma separated): {self._available_topics}. 
                         Use the resources only available among topics 
                         provided in the prompt."),
            ("user", "{input}")
        ])
```

Following output been given:

```
I'm afraid there aren't any topics related to quantum mechanics among the 
ones listed. However, I can help you narrow down your options based on the 
interests and themes represented.

If you're interested in computer science or programming, topics like 
"Proxmox VE Helper-Scripts", "The Evolution of a Scheme Programmer", 
"Translation of Rust's core and alloc crates to Coq for formal verification", 
and "Making a Postgres query 1k times faster" might be more relevant to your 
interests.

On the other hand, if you're interested in technology or engineering, 
topics like "Karman Alpha: amateur rocketry attempt to 100k ft 
(33 minute documentary) [video]", "A low budget consumer hardware espionage 
implant (2018)", and "Raspberry Pi Ltd is considering an IPO" might be more 
appealing.

If none of these topics interest you, I can try to provide some suggestions 
based on the themes represented. For example, if you're interested in 
learning something new, you might enjoy "Strangely Curved Shapes Break 
50-Year-Old Geometry Conjecture", which explores a fascinating 
mathematical concept. If you're looking for something more light-hearted, 
you could consider "Hearing Is Be-Leafing: Students Invent Quieter Leaf Blower", which showcases some creative problem-solving.

Let me know if any of these options appeal to you, or if you'd like me to 
generate some new suggestions based on your interests!
```

That looked better, since the model informed us that no articles (topics) scraped from HackerNews were about Quantum Mechanics (mind we scraped only 10 pages). It still provided us the additional data, which we haven’t asked for though.

Let’s check the system against a topic which we know for sure existed in HackerNews. I have modified the prompt to following:

```
print(chain.invoke({"input": "I would like to read about Raspberry PI"}))
```

Llama3 responded:
```
Raspberry Pi!

Let's dive into some interesting topics related to Raspberry Pi:

1. **Raspbian OS**: The official operating system for Raspberry Pi. You can learn more about its features, customization options, and how to install it.
2. **GPIO pin usage**: As you mentioned, GPIO (General Purpose Input/Output) pins are used to connect various peripherals to your Raspberry Pi. I can provide tips on how to use them effectively.
3. **Raspberry Pi Ltd considering an IPO**: This is a recent development that could have implications for the future of Raspberry Pi.
4. **RPiTX: Radio transmission from a Raspberry Pi GPIO pin**: A fascinating project that demonstrates how you can transmit radio signals using a Raspberry Pi and some custom hardware.

Which one of these topics would you like to explore further?
```

Which is a success, we got expected output from our LLM-powered recommendation system.


# Summary
In this article, we explored the development of a personalized tech-news recommendation system that leverages modern AI tools and efficient data handling techniques. The project integrates several key components: a web scraper using Scrapy, intermediate data storage with Redis, and personalized content recommendations powered by the LLAMA3 model through Ollama.

Within this simple example, we’ve seen potential problems which we’ll be facing when integrating large language models into production:

not fully precise prompts which may lead to unexpected output
difficulties in interpreting what user really wanted
a clear vision on future testing environemnts, which will be responsible for defining deterministic behavior of LLM
But still, I’m impressed how powerful those tools are and how much can be achieved with couple of lines of code.
