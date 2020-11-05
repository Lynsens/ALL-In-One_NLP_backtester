import requests
import time, re, os, sys
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import Chrome
from datetime import datetime, timedelta
import itertools, collections


import os, sys, inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
publisher_dir = os.path.dirname(current_dir)
channel_dir = os.path.dirname(publisher_dir)
text_obtainer_dir = os.path.dirname(channel_dir)
sys.path.insert(0, text_obtainer_dir)
import logger


def get_articles(driver, output_dir):
    url_storage_dir_prefix = output_dir + 'article_urls/'
    article_storage_dir_prefix = output_dir + 'articles/'
    logger_dir = output_dir + 'logs/'
    log_filename = 'articles_log.txt'

    if not os.path.exists(article_storage_dir_prefix):
        os.makedirs(article_storage_dir_prefix)

    url_file_list = os.listdir(url_storage_dir_prefix)
    url_file_list = [i for i in url_file_list if os.stat(url_storage_dir_prefix + i).st_size != 0]
    url_file_list = sorted(url_file_list)

    article_url_prefix = 'https://www.wsj.com/articles/'

    for an_url_file in url_file_list:
        a_date = an_url_file[:-4]
        article_storage_dir = article_storage_dir_prefix + '/' + a_date + '/'
        if not os.path.exists(article_storage_dir):
            os.makedirs(article_storage_dir)

        with open(url_storage_dir_prefix + an_url_file) as url_f:
            article_url_list = [i for i in url_f]


        url_counter = 0
        for an_article_url_suffix in article_url_list:
            an_article_url = article_url_prefix + an_article_url_suffix
            driver.get(an_article_url)
            soup = BeautifulSoup(driver.page_source, 'lxml')

            quote_tags = soup.find_all('a', href=True)
            quote_list = []
            for i in quote_tags:
                url = i['href']
                text = i.text
                if 'market-data/quotes/' in url and len(url.split('/')) == 6:
                    quote_list.append(text)

            content_tag = soup.find("div", {"class":"article-content"})
            try:
                content = content_tag.get_text().strip()
            except AttributeError as e:
                error_log = f"{a_date}'s {an_article_url} failed during content retrieval due to {e}."
                logger.register_log(error_log, logger_dir, log_filename)
                continue

            with open(article_storage_dir + an_article_url_suffix + '-quotes.txt', 'w+') as quote_f:
                quote_f.write('\n'.join(quote_list))

            with open(article_storage_dir + an_article_url_suffix + '.txt', 'w+') as content_f:
                content_f.write(content)

            url_counter += 1
            output_log = f"{a_date}'s {an_article_url_suffix} done (quotes: {len(quote_list)}; content: {len(content)}) | #{url_counter}/{len(article_url_list)}"
            logger.register_log(output_log, logger_dir, log_filename)
