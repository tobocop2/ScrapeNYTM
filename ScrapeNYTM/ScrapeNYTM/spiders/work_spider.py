from scrapy.spider import Spider
from ScrapeNYTM.items import ScrapeNYTMItem
from scrapy.http import Request
from bs4 import BeautifulSoup
from validate_email import validate_email
from urlparse import urlsplit,urlparse
from buzzwords import buzzwords
import re
import requests

START_URL_FMT = 'https://nytm.org/made?list=true&page={}'
extensions = ['jpg,','example','png', 'jpeg', 'pdf', 'tar','exe','zip','gmail','GMAIL','yahoo','YAHOO','hotmail']

class work_spider(Spider):
    name = "nytm"
    allowed_domains = []
    crawled_links = []
    #stats = {}

    def start_requests(self):
        res = requests.get('https://nytm.org/made?list=true&page=1')
        soup = BeautifulSoup(res.text)
        num_pages = int(soup.select('.digg_pagination a')[-2].text)+1
        for num in range(1,num_pages):
        #for num in range(1,2):
            url = START_URL_FMT.format(num)
            yield Request(url,callback=self.parse_page)

    def parse_page(self, response):
        soup = BeautifulSoup(response.body)
        urls = [url['href'] for url in soup.select('.made-listing a')]
        for url in urls:
            if not url in self.crawled_links:
                self.crawled_links.append(url)
                domain = urlparse(url).netloc
                self.allowed_domains.append(domain)
                #self.stats[domain] = {'num_parsed': 0, 'num_pages': 0}
                yield Request(url,callback=self.parse_company,meta={'domain': domain},dont_filter=True)

    def parse_company(self, response):
        domain = response.meta['domain']
        item = ScrapeNYTMItem()
        item['emails'] = []
        item['num_parsed'] = 0
        item['domain'] = domain

        parts = urlsplit(response.url)
        base_url = "{0.scheme}://{0.netloc}".format(parts)

        soup = BeautifulSoup(response.body)
        urls = [url['href'] for url in soup.find_all('a') if url.has_attr('href') and not any(ext in url for ext in extensions)]
        #print urls
        num_pages = len(urls)
        item['num_pages'] = num_pages
        #self.stats[domain]['num_pages'] = num_pages

        for url in urls:
            url_parts = urlsplit(url)
            if not urlparse(url).netloc:
                url = base_url+url
            elif not url.startswith('http'):
                url = url_parts.scheme+url
            netloc = urlparse(url).netloc
            if netloc in self.allowed_domains:
                if not url in self.crawled_links:
                    self.crawled_links.append(url)
                    meta = {'item': item}
                    yield Request(url,callback=self.parse_url,meta=meta,dont_filter=True)


    def parse_url(self,response):
        item = response.meta['item']

        emails = set()
        soup = BeautifulSoup(response.body)
        intersect = set(buzzwords).intersection(set(response.body.split()))
        if intersect:
            key_words = list(intersect)[3:]
            unfiltered_emails =  set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", response.body, re.I))
            filtered_emails = set([email for email in list(unfiltered_emails) if not any(ext in email for ext in extensions)])
            emails.update(filtered_emails)
            item['emails'].append
            ({
                'response_url': response.url,
                'email_list': list(emails),
                'keywords': key_words
            })

        #self.stats[domain]['num_parsed'] += 1
        item['num_parsed'] += 1
        #if item['num_parsed'] == item['num_pages']:
        if item['num_parsed'] == 100 or item['num_parsed'] == item['num_pages']:
        #if self.stats[domain]['num_parsed'] == self.stats[domain]['num_pages']:
            print item
            yield item
