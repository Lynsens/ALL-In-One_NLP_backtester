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


def get_market_data_tags(driver, company_market_url):
    driver.get(company_market_url)
    soup = BeautifulSoup(driver.page_source, 'lxml')

    try:
        target_tag = soup.find("div", {"class": "WSJTheme--title--8uZ7oFS7"})
        ticker_exchange_tag = target_tag.find("span")
        legal_full_name_tag = target_tag.find("h1")
    except AttributeError as e:
        ticker_exchange_tag = None
        legal_full_name_tag = None

    return ticker_exchange_tag, legal_full_name_tag

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

    with open(market_data_output_dir + 'raw_company_market_LUT.json', 'w+') as output_f:
        json.dump(quote_dict, output_f, indent = 4)


def register_tags_to_LUT(company_market_LUT, raw_company_market_LUT, ticker_exchange_tag, legal_full_name_tag, a_company, an_url, output_dir):
    logger_dir = output_dir + 'logs/'
    log_filename = 'WSJ_market_data_log.txt'

    valid_company_flag = True
    try:
        ticker_exchange_text = ticker_exchange_tag.get_text().strip()
        ticker_text = ticker_exchange_text.split('(')[0].strip()
        exchange_text = ticker_exchange_text.split('(')[1][:-1].strip()
    except AttributeError as e:
        ticker_text = 'ticker not on stock market'
        exchange_text = 'exchange not on stock market'
        valid_company_flag = False
    try:
        legal_full_name_text = legal_full_name_tag.get_text().strip()
    except AttributeError as e:
        legal_full_name_text = 'legal full name not on stock market'
        valid_company_flag = False

    US_market_flag = True
    if valid_company_flag == True:
        if 'U.S.' not in exchange_text:
            valid_company_flag = False
            US_market_flag = False

    if valid_company_flag == True:
        company_market_LUT[a_company] = dict()
        company_market_LUT[a_company]['market_data_url'] = an_url
        company_market_LUT[a_company]['ticker'] = ticker_text
        company_market_LUT[a_company]['exchange'] = exchange_text
        company_market_LUT[a_company]['legal_full_name'] = legal_full_name_text
        company_market_LUT[a_company]['quoted_in'] = raw_company_market_LUT[a_company]['quoted_in']

        log_msg = f"{a_company} successfully registered with information from {an_url} (quoted {len(company_market_LUT[a_company]['quoted_in'])}): ticker: {company_market_LUT[a_company]['ticker']}, exchange: {company_market_LUT[a_company]['exchange']}, legal_full_name: {company_market_LUT[a_company]['legal_full_name']}."
        logger.register_log(log_msg, logger_dir, log_filename)

        return company_market_LUT

    else:
        error_logged_flag = False
        if None in [ticker_exchange_tag, legal_full_name_tag]:
            error_log_msg = f"{a_company} failed to register with {an_url} due to ticker_exchange: {ticker_exchange_tag}, legal_full_name: {legal_full_name_tag}"
            logger.register_log(error_log_msg, logger_dir, log_filename)
            error_logged_flag = True

        if US_market_flag == False:
            error_log_msg = f"{a_company} failed to register with {an_url} since exchange being non-US: {exchange_text}."
            logger.register_log(error_log_msg, logger_dir, log_filename)
            error_logged_flag = True

        if error_logged_flag == False:
            error_log_msg = f"{a_company} failed to register with {an_url} for unknown reasons."
            logger.register_log(error_log_msg, logger_dir, log_filename)

        return False

def get_market_data_via_WSJ(driver, output_dir, retry_limit = 1, scale_serp_api_key = None):
    market_data_output_dir = output_dir + 'market_data/'
    logger_dir = output_dir + 'logs/'
    log_filename = 'WSJ_market_data_log.txt'

    with open(market_data_output_dir + 'raw_company_market_LUT.json', 'r') as LUT_f:
        raw_company_market_LUT = json.load(LUT_f)

    company_market_LUT = dict()
    checked_url_list = []
    for (a_company, v) in raw_company_market_LUT.items():

        for an_url in v['url']:
            if an_url in checked_url_list:
                continue


            retry_counter = 0
            while True:
                ticker_exchange_tag, legal_full_name_tag = get_market_data_tags(driver, an_url)
                retry_counter += 1
                if None not in [ticker_exchange_tag, legal_full_name_tag] or retry_counter > retry_limit:
                    break
            checked_url_list.append(an_url)

            updated_LUT = register_tags_to_LUT(company_market_LUT, raw_company_market_LUT, ticker_exchange_tag, legal_full_name_tag, a_company, an_url, output_dir)

            if updated_LUT is not False:
                company_market_LUT = updated_LUT
                break


    with open(market_data_output_dir + 'company_market_LUT.json', 'w') as output_f:
        json.dump(company_market_LUT, output_f, indent = 4)


def get_market_data_via_google(a_company, google_search_result_collect_limit, scale_serp_api_key):
    search_term_suffix = " WSJ market data site: www.wsj.com"
    search_term = "\"" + a_company + "\"" + search_term_suffix
    params = {
          'api_key': scale_serp_api_key,
          'q': search_term
    }

    api_result = requests.get('https://api.scaleserp.com/search', params)
    api_result = api_result.json()
    entry_candidates = api_result['organic_results']

    url_candidates = []
    for an_entry in entry_candidates:
        if 'www.wsj.com/market-data/quotes' in an_entry['link']:
            url_candidates.append(an_entry['link'])


    log_msg = f"{a_company} has extended with {len(url_candidates[:google_search_result_collect_limit])} ({len(url_candidates)} available) candidate urls (from Google)."
    return url_candidates[:google_search_result_collect_limit], log_msg
