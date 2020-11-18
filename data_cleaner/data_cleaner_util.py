import json
from collections import defaultdict
import string

import os, sys, inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
project_dir = os.path.dirname(current_dir)
sys.path.insert(0, project_dir)
import logger


def collect_company_mention_stats(task_dir, text_folder = 'articles', market_data_folder = 'market_data', LUT_filename = 'company_market_LUT', log_filename = 'WSJ_data_cleaner_util_log'):
    logger_dir = task_dir + 'logs/'
    log_filename = log_filename + '.txt'

    LUT_dir = task_dir + market_data_folder + '/' + LUT_filename + '.json'
    with open(LUT_dir, 'r') as LUT_f:
        LUT_data = json.load(LUT_f)

    for v in LUT_data.values():
        v['mentioned_in'] = dict()


    article_storage_dir = task_dir + text_folder + '/'
    article_content_folders = os.listdir(article_storage_dir)
    article_content_folders = [i for i in article_content_folders if os.stat(article_storage_dir + i).st_size != 0]

    for an_article_date_folder in article_content_folders:
        article_list = os.listdir(article_storage_dir + an_article_date_folder)

        for an_article in article_list:
            article_full_dir = article_storage_dir + an_article_date_folder + '/'
            an_article_file_path = article_full_dir + an_article
            with open(an_article_file_path, 'r') as article_f:
                article_json = json.load(article_f)
                article_json['mention'] = dict()

            for a_company in LUT_data.keys():
                a_company_mentioned_feq = str(article_json['content']).count(str(a_company))
                a_company_mentioned_deduction = 0
                for letter in string.ascii_lowercase:
                    a_company_mentioned_deduction += str(article_json['content']).count(str(a_company) + letter)
                    a_company_mentioned_deduction += str(article_json['content']).count(letter + str(a_company))

                # content = str(article_json['content']).lower()
                # content_no_punctu = content.translate(str.maketrans('', '', string.punctuation))


                a_company_mentioned_feq -= a_company_mentioned_deduction


                if a_company_mentioned_feq > 0:
                    article_json['mention'][a_company] = a_company_mentioned_feq
                    # LUT_data[a_company]['mentioned_in'][article_json['article_id']] = LUT_data[a_company]['mentioned_in'][article_json['article_id']] + a_company_mentioned_feq
                    LUT_data[a_company]['mentioned_in'][article_json['article_id']] = {'mentioned_time': article_json['mention'][a_company], 'date': article_json['date']}

                    log_msg = f"Registered {an_article_file_path} mentions of {a_company} for {article_json['mention'][a_company]} times."
                    logger.register_log(log_msg, logger_dir, log_filename)
                else:
                    unfound_msg = f"Found {an_article_file_path} has no ({a_company_mentioned_feq}) mention of {a_company}."
                    # logger.register_log(unfound_msg, logger_dir, log_filename)
                    continue

            with open(an_article_file_path, 'w+') as article_f_n:
                json.dump(article_json, article_f_n, indent = 4)

            log_msg = f"Rewrite {an_article_file_path} with updated mention data."
            logger.register_log(log_msg, logger_dir, log_filename)

    with open(LUT_dir, 'w+') as LUT_f_n:
        json.dump(LUT_data, LUT_f_n, indent = 4)

    log_msg = f"Rewrite {LUT_dir} with updated mentioned_in data."
    logger.register_log(log_msg, logger_dir, log_filename)


