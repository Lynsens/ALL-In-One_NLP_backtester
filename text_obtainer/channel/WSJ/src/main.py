import os
import requests
import time, re
import json
import itertools, collections

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import Chrome
from datetime import datetime, timedelta

import archive_url_scraper
import article_scraper

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
options = webdriver.ChromeOptions()
options.add_argument('headless')
driver = webdriver.Chrome(options=options)

setting_file_path = os.path.join(os.path.dirname(__file__), os.pardir, 'setting.json')
with open(setting_file_path) as setting_f:
    setting = json.load(setting_f)

output_dir = './text_obtainer_output/' + setting['dir']['output_prefix'] + '_' + setting['duration']['start_time'] + '_' + setting['duration']['end_time'] + '/'
setting['dir']['output_dir'] = output_dir
if not os.path.exists(output_dir):
    os.makedirs(output_dir)


archive_url_scraper.login(driver, setting['token'])
archive_url_scraper.get_article_urls(driver, setting['duration'], setting['dir']['output_dir'])

article_scraper.get_articles(driver, setting['dir']['output_dir'])

print(setting)