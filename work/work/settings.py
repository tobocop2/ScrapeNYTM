# -*- coding: utf-8 -*-

# Scrapy settings for work project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'work'

SPIDER_MODULES = ['work.spiders']
NEWSPIDER_MODULE = 'work.spiders'
DEPTH_LIMIT = 100

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'work (+http://www.yourdomain.com)'
