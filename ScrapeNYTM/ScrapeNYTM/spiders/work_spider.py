from scrapy.spider import Spider
from ScrapeNYTM.items import ScrapeNYTMItem
#from xtr33m.items import band_item
from scrapy.http import Request
from bs4 import BeautifulSoup
from validate_email import validate_email
from urlparse import urlsplit,urlparse
from buzzwords import buzzwords
import re
import requests
import inspect

START_URL_FMT = 'https://nytm.org/made?list=true&page={}'
extensions = ['jpg,','example','png', 'jpeg', 'pdf', 'tar','exe','zip','gmail','GMAIL','yahoo','YAHOO','hotmail']

class work_spider(Spider):
    name = "nytm"
    allowed_domains = []
    crawled_links = []
    stats = {}

    def start_requests(self):
        res = requests.get('https://nytm.org/made?list=true&page=1')
        soup = BeautifulSoup(res.text)
        num_pages = int(soup.select('.digg_pagination a')[-2].text)+1
        for num in range(1,num_pages):
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
                self.stats[domain] = {'num_parsed': 0, 'num_pages': 0}
                yield Request(url,callback=self.parse_company,meta={'domain': domain})

    def parse_company(self, response):
        item = ScrapeNYTMItem()
        item['emails'] = []

        parts = urlsplit(response.url)
        base_url = "{0.scheme}://{0.netloc}".format(parts)
        domain = response.meta['domain']

        soup = BeautifulSoup(response.body)
        urls = [url['href'] for url in soup.find_all('a') if url.has_attr('href')]
        num_pages = len(urls)
        self.stats[domain]['num_pages'] = num_pages

        for url in urls:
            url_parts = urlsplit(url)
            path = url[:url.rfind('/')+1] if '/' in url_parts.path else url
            netloc = urlparse(url).netloc
            if url.startswith('/'):
               url = base_url + url
            elif not url.startswith('http'):
               url = path + url
            if not url in self.crawled_links:
                self.crawled_links.append(url)
                meta = {'domain': domain,'item': item}
                if netloc in self.allowed_domains:
                    yield Request(url,callback=self.parse_url,meta=meta)


    def parse_url(self,response):
        item = response.meta['item']
        domain = response.meta['domain']

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

        self.stats[domain]['num_parsed'] += 1
        if self.stats[domain]['num_parsed'] == self.stats[domain]['num_pages']:
            yield item
        return
