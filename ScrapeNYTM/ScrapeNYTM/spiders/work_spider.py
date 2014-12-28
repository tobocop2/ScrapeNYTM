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
    stats = {}
    crawled_links = []

    def start_requests(self):
        res = requests.get('https://nytm.org/made?list=true&page=1')
        soup = BeautifulSoup(res.text)
        num_pages = int(soup.select('.digg_pagination a')[-2].text)+1
        for num in range(1,num_pages):
            url = START_URL_FMT.format(num)
            yield Request(url,callback=self.parse)

    def parse(self, response):
        soup = BeautifulSoup(response.body)
        urls = [url['href'] for url in soup.select('.made-listing a')]
        for url in urls:
            if not url in self.crawled_links:
                self.crawled_links.append(url)
                item = ScrapeNYTMItem()
                item['emails'] = []
                emails = set()
                domain = urlparse(url).netloc
                self.allowed_domains.append(domain)
                self.stats[domain] = 0
                meta = {
                        'item': item,
                        #'crawled_links': crawled_links,
                        'emails': emails
                }
                yield Request(url,callback=self.parse_job,meta=meta)

    def parse_job(self,response):
        item = response.meta['item']
        #crawled_links = response.meta['crawled_links']
        emails = response.meta['emails']
        soup = BeautifulSoup(response.body)
        parts = urlsplit(response.url)
        base_url = "{0.scheme}://{0.netloc}".format(parts)
        path = response.url[:response.url.rfind('/')+1] if '/' in parts.path else response.url
        intersect = set(buzzwords).intersection(set(response.body.split()))
        if intersect:
            keys = str(intersect)[3:]
            tmp_emails =  set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", response.body, re.I))
            email_set = set([email for email in list(tmp_emails) if not any(ext in email for ext in extensions)])
            emails.update(email_set)
            print emails
            item['emails'].append({
                'response_url': response.url,
                'email_list': list(emails),
                'keywords': keys
            })

        for anchor in soup.find_all('a'):
            link = anchor.attrs["href"] if "href" in anchor.attrs else ''

            if link.startswith('/'):
               link = base_url + link
            elif not link.startswith('http'):
               link = path + link

            if not link in self.crawled_links:
                self.crawled_links.append(link)
                meta = {
                        'item': item,
                        #'crawled_links': crawled_links,
                        'emails': emails
                }
                domain = urlparse(link).netloc
                if domain in self.allowed_domains:
                    print 'in allowed domains:\t'+domain
                    if self.stats[domain] <= 50:
                        self.stats[domain] += 1
                        yield Request(link,callback=self.parse_job,meta=meta)
                    else:
                        print 'The domain count here is:  %d' % self.stats[domain]
                        print 'yielding item with domain %s' % domain
                        print 'yielding item with domain %s' % domain
                        print 'yielding item with domain %s' % domain
                        print 'yielding item with domain %s' % domain
                        print 'yielding item with domain %s' % domain
                        item['domain'] = domain
                        yield item
            #if link has been crawled already
            #print 'This link has been crawled: %s' % link
            #return
