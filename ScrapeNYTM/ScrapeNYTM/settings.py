# -*- coding: utf-8 -*-

# Scrapy settings for work project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'ScrapeNYTM'

SPIDER_MODULES = ['ScrapeNYTM.spiders']
NEWSPIDER_MODULE = 'ScrapeNYTM.spiders'
COOKIES_ENABLED = 0
DOWNLOAD_DELAY =  0
RETRY_TIMES = 5

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'work (+http://www.yourdomain.com)'

