from scrapy.spider import Spider
from ScrapeNYTM.items import ScrapeNYTMItem
from scrapy.http import Request
from bs4 import BeautifulSoup
from urlparse import urlsplit,urlparse
from buzzwords import buzzwords
import re
import requests

START_URL_FMT = 'https://nytm.org/made?list=true&page={}'
extensions = ['jpg,','example','png', 'jpeg', 'pdf', 'tar','exe','zip','gmail','yahoo','hotmail']

class work_spider(Spider):
    name = "nytm"
    #only allow nytm company domains
    allowed_domains = []
    #ensure that no link is crawled twice
    crawled_links = []

    def start_requests(self):
        res = requests.get('https://nytm.org/made?list=true&page=1')
        soup = BeautifulSoup(res.text)
        num_pages = int(soup.select('.digg_pagination a')[-2].text)+1
        for num in range(1,num_pages):
            url = START_URL_FMT.format(num)
            yield Request(url,callback=self.parse_nytm_page)

    def parse_nytm_page(self, response):
        #Go through each nytm page, initialize scrapy item, and then crawl company page
        soup = BeautifulSoup(response.body)
        urls = [url['href'] for url in soup.select('.made-listing a')]
        for url in urls:
            if not url in self.allowed_domains:
                self.crawled_links.append(url)
                domain = urlparse(url).netloc
                self.allowed_domains.append(domain)
                item = ScrapeNYTMItem()
                item['emails'] = []
                item['num_parsed'] = 0
                item['num_pages'] = 0
                item['domain'] = domain
                item['urls'] = set()
                meta = {'item': item}
                #self.stats[domain] = {'num_parsed': 0, 'num_pages': 0}
                yield Request(url,callback=self.parse_company,meta=meta,dont_filter=True)

    def parse_company(self, response):
        #parse all urls within company repsonse body
        item = response.meta['item']
        parts = urlsplit(response.url)
        base_url = "{0.scheme}://{0.netloc}".format(parts)

        soup = BeautifulSoup(response.body)
        urls = [url['href'] for url in soup.find_all('a') if url.has_attr('href') and not any(ext in url for ext in extensions)]
        #find new urls on company page at each recursion level and only iterate through these
        #url_difference = set(urls).difference(item['urls'])

        #update url set to include any new urls found from within company page. Then update the total page count
        item['urls'].update(urls)
        item['num_pages'] = len(item['urls'])

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
        #Check to see if any of the buzzwords are found on the page
        intersect = set(buzzwords).intersection(set(response.body.split()))
        if intersect:
            key_words = list(intersect)[3:]
            #Build emal set ad flter out unwanted emals
            unfiltered_emails =  set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", response.body, re.I))
            filtered_emails = set([email for email in list(unfiltered_emails) if not any(ext in email for ext in extensions)])
            emails.update(filtered_emails)
            item['emails'].append
            ({
                'response_url': response.url,
                'email_list': list(emails),
                'keywords': key_words
            })

        item['num_parsed'] += 1
        if item['num_parsed'] == 500 or item['num_parsed'] == item['num_pages']:
            print item
            yield item
        yield Request(response.url,callback=self.parse_company,meta={'item': item})
