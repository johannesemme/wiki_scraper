import scrapy
from scrapy import Request
import json
import os
from bs4 import BeautifulSoup
from tqdm import tqdm
import re
import re
import logging

logger = logging.getLogger('wiki_scraper')

class MySpider(scrapy.Spider):
    name = 'wiki'
    allowed_domains = ['https://da.wikipedia.org/wiki/']  # Replace with your target domain(s)

    def __init__(self, depth=3, *args, **kwargs):
        super(MySpider, self).__init__(*args, **kwargs)

        # get args from command line
        self.depth = int(depth)

        # load data
        try:
            with open(f"data/urls_depth_{self.depth}.json", "r") as f:
                data = dict(json.load(f))
        except:
            raise ValueError(f"Could not find data/urls_depth_{self.depth}.json. Please run collect_wiki_urls.py with the same depth argument first")

        # make folder: wiki_depth_{depth} and subfolders for each category
        if not os.path.exists(f"data/wiki_depth_{self.depth }"):
            os.mkdir(f"data/wiki_depth_{self.depth }")

        for category in data.keys():
            if not os.path.exists(f"data/wiki_depth_{self.depth }/{category}"):
                os.mkdir(f"data/wiki_depth_{self.depth }/{category}")

        self.data = data

    def start_requests(self):
        for category, urls in self.data.items():
            for url in tqdm(urls, desc=f"Category: {category}"):
                # don't filter as we want to visit the same url multiple times (a url can be in multiple categories)
                yield Request(url=url, callback=self.parse, meta={'category': category}, dont_filter=True, errback=self.errback_httpbin) 

    def errback_httpbin(self, failure):
        # log all failures
        self.logger.error(repr(failure))
        # log url that failed
        self.logger.error(failure.request.url)
        # reason
        self.logger.error(failure.value)

    def parse(self, response):
        category = response.meta['category']

        # log if no response
        if response.status != 200:
            self.logger.info(f"Failed to get {response.url}")
            logger.info(f"Failed to get {response.url}")
            return

        url = response.url if response.url else None
        html = response.text if response.text else None

        # get title
        title = None
        try:
            title = response.css(".mw-page-title-main::text").get()
            save_title = title.replace('/', '_')
        except:
            # if first attempt failed, try to get title from the first h1 (id = firstHeading)
            try:
                title = response.xpath('//h1//text()').get()
                save_title = title.replace('/', '_')
            except:
                title = None

        if not title:
            title = url.split('https://da.wikipedia.org/wiki/')[-1].replace('/', '_')
            save_title = title.replace('/', '_')
            logger.info(f"Could not get title for url: {url}. Using {title} derived from url")

        # remove all tbody (table text), image captions and dd tags (references)
        text = None
        try:
            soup = BeautifulSoup(html, 'html.parser')
            text = soup.findAll('div',attrs={'id':"mw-content-text"})[0]
            for tbody in text.findAll('tbody'): # remove all tables
                tbody.decompose()
            for div in text.findAll('div',attrs={'class':"thumbcaption"}): # remove all captions for images
                div.decompose()    
            for dd in text.findAll('dd'):
                dd.decompose()
            text = text.prettify()
        except:
            logger.info("Error in parsing html")

        try:
            # remove all non-alphanumeric characters from save_title
            save_title = re.sub(r'\W+', '', save_title)
            with open(f"data/wiki_depth_{self.depth}/{category}/{save_title}.txt", "w", encoding="utf-8") as f:
                # save title, text, category and url in txt file on same line
                f.write(title + "\t" + url + "\t" + category + "\t" + text + "\n")
        except:
            logger.info("Error in saving data for url: ", url)










