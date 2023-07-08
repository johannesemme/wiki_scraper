import scrapy
from scrapy.pipelines.files import FilesPipeline
from scrapy import Request
#from my_scraper.items import MyItem
import json
import os
from bs4 import BeautifulSoup
from tqdm import tqdm
import logging

logger = logging.getLogger('wiki_scraper')

class MySpider(scrapy.Spider):
    name = 'wiki'
    allowed_domains = ['https://da.wikipedia.org/wiki/']  # Replace with your target domain(s)

    def __init__(self, depth=1, *args, **kwargs):
        super(MySpider, self).__init__(*args, **kwargs)

        # get args from command line
        self.depth = int(depth)

        # load data
        with open(f"../data/urls_depth_{self.depth}.json", "r") as f:
            data = dict(json.load(f))

        # make folder: wiki_depth_{depth} and subfolders for each category
        if not os.path.exists(f"../data/wiki_depth_{self.depth }"):
            os.mkdir(f"../data/wiki_depth_{self.depth }")
        for category in data.keys():
            if not os.path.exists(f"../data/wiki_depth_{self.depth }/{category}"):
                os.mkdir(f"../data/wiki_depth_{self.depth }/{category}")
        self.data = data

    def start_requests(self):
        for category, urls in self.data.items():
            for url in tqdm(urls, desc=f"Category: {category}"):
                # don't filter to avoid duplicates in case of error (e.g. timeout)
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
        try:
            title = response.css(".mw-page-title-main::text").get().replace('/', '_')
        except:
            title = None
        if not title:
            title = url.split('https://da.wikipedia.org/wiki/')[-1].replace('/', '_')

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
        
        # save data
        try:
            with open(f"../data/wiki_depth_{self.depth}/{category}/{title}.txt", "w") as f:
                # save title, text, category and url in txt file on same line
                f.write(title + "\t" + url + "\t" + category + "\t" + text + "\n")
        except:
            logger.info("Error in saving data for url: ", url)










