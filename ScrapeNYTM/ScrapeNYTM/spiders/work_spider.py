from scrapy.spider import Spider
from ScrapeNYTM.items import ScrapeNYTMItem
from scrapy.http import Request
from urlparse import urlsplit,urlparse
from buzzwords import buzzwords,extensions
from user_agents import user_agents
import random
import urllib2
import re


class work_spider(Spider):
    name = "nytm"
    #only allow nytm company domains
    allowed_domains = []
    #ensure that no link is crawled twice
    crawled_links = []

    def start_requests(self):
        START_URL_FMT = 'https://nytm.org/made?list=true&page={}'
        user_agent = random.choice(user_agents)
        url = 'https://nytm.org/made?list=true&page=1'
        headers={'User-Agent':user_agent}
        req = urllib2.Request('https://nytm.org/made?list=true&page=1',headers=headers)
        res = urllib2.urlopen(req).read()
        num_pages = int(re.findall('page=[0-9]+',res)[-2][-2:])
        #for num in range(1,num_pages):
        for num in range(1,2):
            url = START_URL_FMT.format(num)
            yield Request(url,callback=self.parse_nytm_page)

    def parse_nytm_page(self, response):
        #Go through each nytm page, initialize scrapy item, and then crawl company page
        urls = response.css('.made-listing a::attr(href)').extract()
        for url in urls:
            if not url in self.allowed_domains:
                self.crawled_links.append(url)
                domain = urlparse(url).netloc
                print domain
                self.allowed_domains.append(domain)
                item = ScrapeNYTMItem()
                item['emails'] = []
                item['num_parsed'] = 0
                item['num_pages'] = 1
                item['domain'] = domain
                #item['urls'] = set()
                url_set = set()
                meta = {'item': item, 'url_set': url_set}
                #self.stats[domain] = {'num_parsed': 0, 'num_pages': 0}
                yield Request(url,callback=self.parse_company,meta=meta,dont_filter=True)

    def parse_company(self, response):
        #parse all urls within company repsonse body
        item = response.meta['item']
        url_set = response.meta['url_set']
        parts = urlsplit(response.url)
        base_url = "{0.scheme}://{0.netloc}".format(parts)

        urls = response.css('a::attr(href)').extract()
        #find new urls on company page at each recursion level and only iterate through these
        #url_difference = set(urls).difference(item['urls'])

        #update url set to include any new urls found from within company page. Then update the total page count
        url_set.update(urls)
        item['num_pages'] = len(url_set)

        for url in urls:
            if any(ext in url for ext in extensions):
                continue
            url_parts = urlsplit(url)
            if not urlparse(url).netloc:
                url = base_url+url
            elif not url.startswith('http'):
                url = 'http'+url
            netloc = urlparse(url).netloc
            if netloc in self.allowed_domains:
                if not url in self.crawled_links:
                    self.crawled_links.append(url)
                    item['num_parsed'] += 1
                    meta = {'item': item, 'url_set': url_set}
                    yield Request(url,callback=self.parse_url,meta=meta,dont_filter=True)


    def parse_url(self,response):
        item = response.meta['item']
        url_set = response.meta['url_set']
        emails = set()
#Check to see if any of the buzzwords are found on the page
        intersect = set(buzzwords).intersection(set(response.body.split()))
        if intersect:
            key_words = list(intersect)[3:]
#Build emal set ad flter out unwanted emals
            unfiltered_emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", response.body, re.I))
            filtered_emails = set([email for email in list(unfiltered_emails) if not any(ext in email for ext in extensions)])
            emails.update(filtered_emails)
            item['emails'].append(
                {
                    'response_url': response.url,
                    'email_list': list(emails),
                    'keywords': key_words
                }
            )
        if item['num_parsed'] == 200 or item['num_parsed'] == item['num_pages']:
            print item
            yield item
        else:
            yield Request(response.url,callback=self.parse_company,meta={'item': item, 'url_set': url_set})

