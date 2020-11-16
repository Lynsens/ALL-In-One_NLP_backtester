import json
import copy
import collections

import os, sys, inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
project_dir = os.path.dirname(current_dir)
sys.path.insert(0, project_dir)
import logger
import data_cleaner.sentiment_analyzer as sentiment_analyzer

output_dir = "./text_obtainer_output/WSJ_20120102_20120103/"


def collect_mentioned_articles(task_dir, market_data_folder = 'market_data', LUT_filename = 'company_market_LUT', log_filename = 'WSJ_dummy_model_log'):
    logger_dir = task_dir + 'logs/'
    log_filename = log_filename + '.txt'

    LUT_dir = task_dir + market_data_folder + '/' + LUT_filename + '.json'
    with open(LUT_dir, 'r') as LUT_f:
        LUT_data = json.load(LUT_f)

    mentioned_article_dict = dict()
    for v in LUT_data.values():
        for an_article_id, an_article_meta in v['mentioned_in'].items():
            mentioned_article_dict[an_article_id] = {'date': an_article_meta['date']}

    return mentioned_article_dict



def collect_article_sentiment_analysis(task_dir, mentioned_article_dict, output_filename = 'mentioned_articles_sentiment_analysis', text_folder = 'articles',  market_data_folder = 'market_data', log_filename = 'WSJ_dummy_model_log'):
    logger_dir = task_dir + 'logs/'
    log_filename = log_filename + '.txt'
    article_storage_dir = task_dir + text_folder + '/'

    sentiment_word_dict = sentiment_analyzer.get_sentiment_word_dict()

    mentioned_article_sentiment_dict = copy.deepcopy(mentioned_article_dict)

    for an_article_id, an_article_meta in mentioned_article_dict.items():
        an_article_path = article_storage_dir + an_article_meta['date'] + '/' + an_article_id + '.json'

        try:
            with open(an_article_path, 'r') as article_f:
                article_json = json.load(article_f)
                article_content = article_json['content']
        except FileNotFoundError:
            error_msg = f"{an_article_id} not found with {an_article_path} (date: {an_article_meta['date']})."
            logger.register_log(error_msg, logger_dir, log_filename)

        an_article_sentiment_analysis_dict = sentiment_analyzer.get_sentiment_analysis(article_content, sentiment_word_dict, most_common_thld = 100)

        mentioned_article_sentiment_dict[an_article_id]['sentiment_analysis'] = an_article_sentiment_analysis_dict
        log_msg = f"Registered {an_article_id} (date: {an_article_meta['date']}) sentiment analysis: {an_article_sentiment_analysis_dict}."
        logger.register_log(log_msg, logger_dir, log_filename)


    output_path = task_dir + market_data_folder + '/' + output_filename + '.json'
    with open(output_path, 'w+') as output_f:
        json.dump(mentioned_article_sentiment_dict, output_f, indent = 4)
    return mentioned_article_sentiment_dict

