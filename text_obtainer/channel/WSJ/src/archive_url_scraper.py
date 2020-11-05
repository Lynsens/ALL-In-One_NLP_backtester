import requests
import time, re
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import Chrome
from datetime import datetime,timedelta
import itertools, collections


import os, sys, inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
publisher_dir = os.path.dirname(current_dir)
channel_dir = os.path.dirname(publisher_dir)
text_obtainer_dir = os.path.dirname(channel_dir)
sys.path.insert(0, text_obtainer_dir)
import logger





def login(driver, token):

    driver.get('https://accounts.wsj.com/login?')
    time.sleep(3)
    driver.find_element_by_xpath("//input[@type='email']").send_keys(token['account'])
    driver.find_element_by_xpath("//input[@type='password']").send_keys(token['password'])
    driver.find_element_by_xpath("//button[@type='submit']").click()

    request_session = requests.Session()
    driver_cookies = driver.get_cookies()
    for c in driver_cookies:
        request_session.cookies.set(c['name'], c['value'])


def get_article_urls(driver, duration, output_dir):
    article_urls_storage_dir = output_dir + 'article_urls/'
    logger_dir = output_dir + 'logs/'
    log_filename = 'article_urls_log.txt'
    if not os.path.exists(article_urls_storage_dir):
        os.makedirs(article_urls_storage_dir)

    from_date = datetime.strptime(duration['start_time'], "%Y%m%d").date()
    to_date = datetime.strptime(duration['end_time'], "%Y%m%d").date()
    delta = to_date - from_date
    date_list = []
    for i in range(delta.days + 1):
        date_list.append(from_date + timedelta(days=i))

    archive_url_prefix = 'https://www.wsj.com/news/archive/'
    for a_date in date_list:
        an_archive_url = archive_url_prefix + a_date.strftime("%Y%m%d")

        #     archive_page = request_session.get(a_archive_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'})
        #     time.sleep(archive_load_sleep_time)
        #     soup = BeautifulSoup(archive_page.text, 'lxml')

        daily_article_url_list = []
        try:
            daily_article_url_list = scrape_headline_urls(driver, an_archive_url)
        except AttributeError as e:
            log_msg = f'{a_date.strftime("%Y%m%d")} not retrieved due to {e}.'
            logger.register_log(log_msg, logger_dir, log_filename)
            continue
        while (len(daily_article_url_list) == 0):
            try:
                daily_article_url_list = scrape_headline_urls(driver, an_archive_url)
            except AttributeError as e:
                log_msg = f'{a_date.strftime("%Y%m%d")} not retrieved due to {e}.'
                logger.register_log(log_msg, logger_dir, log_filename)
                break

        with open(article_urls_storage_dir + a_date.strftime("%Y%m%d") + '.txt', 'w+') as f:
            f.write('\n'.join(daily_article_url_list))

        log_msg = f'{a_date.strftime("%Y%m%d")} done, urls to {len(daily_article_url_list)} articles retrieved.'
        logger.register_log(log_msg, logger_dir, log_filename)




def scrape_headline_urls(driver, an_archive_url):
    driver.get(an_archive_url)
    soup = BeautifulSoup(driver.page_source, 'lxml')

    archive_headline_url_tags = soup.find_all('h2', attrs = {'class': 'WSJTheme--headline--unZqjb45'})
    archive_headline_url_list = [i.find('a')['href'] for i in archive_headline_url_tags]


    stripped_archive_headline_url_list = []
    for an_o_url in archive_headline_url_list:
        regex_match = re.search("(SB)\d+", an_o_url)
        if regex_match is None:
            log_msg = f"{a_date.strftime('%Y%m%d')}\'s hyperlink {an_o_url} not logged."
            register_url_log(log_msg)
            continue
        a_stripped_url = regex_match.group(0)
        stripped_archive_headline_url_list.append(a_stripped_url)

    return stripped_archive_headline_url_list

