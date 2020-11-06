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
def collect_quote_list(output_dir):
    article_storage_dir = output_dir + 'articles/'
    market_data_output_dir = output_dir + 'market_data/'
    if not os.path.exists(market_data_output_dir):
        os.makedirs(market_data_output_dir)

    article_content_folders = os.listdir(article_storage_dir)
    article_content_folders = [i for i in article_content_folders if os.stat(article_storage_dir + i).st_size != 0]

    quote_dict = dict()
    for an_article_date_folder in article_content_folders:
        article_list = os.listdir(article_storage_dir + an_article_date_folder)

        for an_article in article_list:
            with open(article_storage_dir + an_article_date_folder + '/' + an_article, 'r+') as article_f:
                article_json = json.load(article_f)

                for company_name, company_wsj_url in article_json['quotes']:
                    if company_name not in quote_dict:
                        quote_dict[company_name] = dict()
                        quote_dict[company_name]['url'] = [company_wsj_url]
                    else:
                        if not company_wsj_url in quote_dict[company_name]['url']:
                            quote_dict[company_name]['url'] = quote_dict[company_name]['url'] + [company_wsj_url]

                    if 'quoted_in' in quote_dict[company_name]:
                        quote_dict[company_name]['quoted_in'] = quote_dict[company_name]['quoted_in'] + [article_json['article_id']]
                    else:
                        quote_dict[company_name]['quoted_in'] = [article_json['article_id']]

    with open(market_data_output_dir + 'company_market_LUT.json', 'w+') as output_f:
        json.dump(quote_dict, output_f, indent = 4)

