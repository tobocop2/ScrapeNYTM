from scrapy.spider import Spider
from work.items import WorkItem
#from xtr33m.items import band_item
from scrapy.http import Request
from bs4 import BeautifulSoup
from validate_email import validate_email
from urlparse import urlsplit,urlparse
import re
import requests
import inspect
#https://nytm.org/
#https://nytm.org/made?list=true&page=1

START_URL_FMT = 'https://nytm.org/made?list=true&page={}'
buzzwords = ['dedicated','cooperative','hiring','hire','job','jobs','career','careers','engineer','engineering','apply','info',\
        'contact','resume','software','software engineering','back end','front end','python','ruby','nodejs','javascript','php',\
        'java','motivated','rails','django','flask','application','developer','programmer','proficient','programmer','computer science',\
        'undergraduate','motivated','javascript','html/css','Carcass','Python/Django','Java','Javascript- Node.JS', 'Angular.JS', \
        'Backbone.JS', 'Knockout.JS', 'JQuery', 'AJAX','HTML5','CSS3','AWS Cloud','Hadoop','Python','MongoDB', 'Machine Learning','Scala',\
        'NoSQL', 'MongoDB','Amazon Web Services','Node.js', 'mySQL', 'SQL Server', 'PostgreSQL', 'Oracle', 'Agile', 'REST', 'JSON', \
        'XML', 'SaaS', 'Cloud','x86 Assembly','6502 Assembly','Full Time','full time','full-time']
extensions = ['png', 'jpeg', 'pdf', 'tar','exe','zip','gmail','GMAIL','yahoo','YAHOO','hotmail']

class work_spider(Spider):
    name = "work"
    allowed_domains = []
    stats = {}

    def start_requests(self):
        res = requests.get('https://nytm.org/made?list=true&page=1')
        soup = BeautifulSoup(res.text)
        num_pages = int(soup.select('.digg_pagination a')[-2].text)+1
        for num in range(1,num_pages):
            url = START_URL_FMT.format(num)
            yield Request(url,callback=self.parse)

    def parse(self, response):

        soup = BeautifulSoup(response.body)
        crawled_links = []
        urls = [url['href'] for url in soup.select('.made-listing a')]
        for url in urls:
            if not url in crawled_links:
                crawled_links.append(url)
                item = WorkItem()
                item['emails'] = []
                emails = set()
                domain = urlparse(url).netloc
                self.allowed_domains.append(domain)
                self.stats[domain] = 1
                meta = {'item': item,'crawled_links': crawled_links,'emails': emails}
                yield Request(url,callback=self.parse_job,meta=meta)

    def parse_job(self,response):
        item = response.meta['item']
        crawled_links = response.meta['crawled_links']
        emails = response.meta['emails']
        soup = BeautifulSoup(response.body)
        parts = urlsplit(response.url)
        base_url = "{0.scheme}://{0.netloc}".format(parts)
        path = response.url[:response.url.rfind('/')+1] if '/' in parts.path else response.url
        intersect = set(buzzwords).intersection(set(response.body.split()))
        if intersect:
            keys = str(intersect)[3:]
            new_emails =  set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", response.body, re.I))
            new_emails = set([email for email in list(new_emails) if not any(ext in email for ext in extensions)])
            emails.update(new_emails)
            print emails
            item['emails'].append({response.url: list(emails),'keywords': keys})

        for anchor in soup.find_all('a'):
            link = anchor.attrs["href"] if "href" in anchor.attrs else ''

            if link.startswith('/'):
               link = base_url + link
            elif not link.startswith('http'):
               link = path + link

            if not link in crawled_links:
                crawled_links.append(link)
                meta = {'item': item,'crawled_links': crawled_links,'emails': emails}
                domain = urlparse(link).netloc
                if domain in self.allowed_domains:
                    self.stats[domain] +=1
                    print 'in allowed domains:\t'+domain
                    if self.stats[domain] <= 50:
                        yield Request(link,callback=self.parse_job,meta=meta)
                    else:
                        #print inspect.currentframe().f_back.f_lineno
                        yield item
