import json
import copy
import collections
from datetime import datetime

import os, sys, inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
project_dir = os.path.dirname(current_dir)
sys.path.insert(0, project_dir)
import logger
import data_cleaner.sentiment_analyzer as sentiment_analyzer

output_dir = "./text_obtainer_output/WSJ_20120101_20120331/"
# output_dir = "./text_obtainer_output/WSJ_20120102_20120103/"


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


def calculate_company_sentiment_stats(task_dir, mentioned_article_sentiment_dict, output_filename = 'company_market_sentiment_LUT', market_data_folder = 'market_data', LUT_filename = 'company_market_LUT', log_filename = 'WSJ_dummy_model_log'):
    logger_dir = task_dir + 'logs/'
    log_filename = log_filename + '.txt'


    LUT_dir = task_dir + market_data_folder + '/' + LUT_filename + '.json'
    with open(LUT_dir, 'r') as LUT_f:
        LUT_data = json.load(LUT_f)
    company_market_sentiment_LUT = copy.deepcopy(LUT_data)

    for v in company_market_sentiment_LUT.values():
        v['sentiment_indicator'] = dict()

    # ZeroDivisionError
    for a_company, a_company_info in LUT_data.items():
        for an_article, an_article_info in a_company_info['mentioned_in'].items():
            an_article_sentiment = mentioned_article_sentiment_dict[an_article]['sentiment_analysis']

            for a_catagory in an_article_sentiment.keys():
                an_article_sentiment[a_catagory] = an_article_sentiment[a_catagory] * an_article_info['mentioned_time']


            if an_article_info['date'] in company_market_sentiment_LUT[a_company]['sentiment_indicator']:
                pre_counter = collections.Counter(company_market_sentiment_LUT[a_company]['sentiment_indicator'][an_article_info['date']])
                current_counter = collections.Counter(an_article_sentiment)
                updated_article_sentiment_dict = dict(pre_counter + current_counter)
                company_market_sentiment_LUT[a_company]['sentiment_indicator'][an_article_info['date']] = updated_article_sentiment_dict
            else:
                company_market_sentiment_LUT[a_company]['sentiment_indicator'][an_article_info['date']] = an_article_sentiment

            log_msg = f"Updated {an_article} (date: {an_article_info['date']}) sentiment analysis to {a_company}: {company_market_sentiment_LUT[a_company]['sentiment_indicator'][an_article_info['date']]}."
            logger.register_log(log_msg, logger_dir, log_filename)


    company_market_sentiment_LUT = add_trade_signal_to_LUT(company_market_sentiment_LUT)



    for a_company, a_company_info in company_market_sentiment_LUT.items():
        company_market_sentiment_LUT[a_company]['total_actionable_days'] = len(a_company_info['sentiment_indicator'].keys())
        company_market_sentiment_LUT[a_company]['total_mentioned_times'] = sum([v['mentioned_time'] for v in a_company_info['mentioned_in'].values()])

        company_market_sentiment_LUT[a_company]['sentiment_indicator'] = {k: v for k, v in sorted(a_company_info['sentiment_indicator'].items(), key = lambda date: datetime.strptime(date[0], "%Y%m%d"))}

    company_market_sentiment_LUT = {k: v for k, v in sorted(company_market_sentiment_LUT.items(), key = lambda x: x[1]['total_actionable_days'], reverse = True)}


    output_path = task_dir + market_data_folder + '/' + output_filename + '.json'
    with open(output_path, 'w+') as output_f:
        json.dump(company_market_sentiment_LUT, output_f, indent = 4)

    log_msg = f"{output_filename} successfully exported to {output_path}."
    logger.register_log(log_msg, logger_dir, log_filename)

    clean_trade_signal_log = extract_clean_trade_signal_log(company_market_sentiment_LUT)
    output_path = task_dir + market_data_folder + '/' + 'clean_trade_signal_log' + '.json'
    with open(output_path, 'w+') as output_f:
        json.dump(clean_trade_signal_log, output_f, indent = 4)
    log_msg = f"clean_trade_signal_log successfully exported to {output_path}."
    logger.register_log(log_msg, logger_dir, log_filename)

    return mentioned_article_sentiment_dict


def add_trade_signal_to_LUT(company_market_sentiment_LUT):

    for a_company_info in company_market_sentiment_LUT.values():
        for a_date, a_date_sentiment in a_company_info['sentiment_indicator'].items():
            a_company_info['sentiment_indicator'][a_date] = generate_trade_signal(a_company_info['sentiment_indicator'][a_date])

    return company_market_sentiment_LUT

def generate_trade_signal(sentiment_indicator_dict, significant_coefficient = 1.2):

    catagory_list = ['negative', 'positive', 'uncertainty', 'litigious', 'strongmodal', 'weakmodal', 'constraining']
    for catagory in catagory_list:
        if catagory not in sentiment_indicator_dict:
            sentiment_indicator_dict[catagory] = 0

    D = copy.deepcopy(sentiment_indicator_dict)
    for catagory in catagory_list:
        D[catagory] += 1


    pos_indicator = D['positive'] + 0.5 * D['strongmodal']
    neg_indicator = D['negative'] + 0.5 * D['constraining']

    sentiment_indicator_dict['trade_info'] = dict()
    sentiment_indicator_dict['trade_info']['trade_indicator'] = (pos_indicator/neg_indicator, (pos_indicator, neg_indicator))


    if pos_indicator > neg_indicator * significant_coefficient:
        sentiment_indicator_dict['trade_info']['trade_signal'] = 'buy'
    elif neg_indicator > pos_indicator * significant_coefficient:
        sentiment_indicator_dict['trade_info']['trade_signal'] = 'sell'
    else:
        sentiment_indicator_dict['trade_info']['trade_signal'] = 'hold'

    return sentiment_indicator_dict

def extract_clean_trade_signal_log(company_market_sentiment_LUT, actional_days_top_N_thld = 5):
    if actional_days_top_N_thld > len(company_market_sentiment_LUT.keys()):
        actional_days_top_N_thld = len(company_market_sentiment_LUT.keys())

    counter = 0
    clean_dict = dict()
    for a_company, a_company_info in company_market_sentiment_LUT.items():
        if counter == actional_days_top_N_thld:
            break

        clean_dict[a_company] = copy.deepcopy(a_company_info)
        del clean_dict[a_company]['quoted_in']
        del clean_dict[a_company]['mentioned_in']
        del clean_dict[a_company]['sentiment_indicator']
        clean_dict[a_company]['sentiment_indicator'] = dict()

        for a_date, a_date_info in a_company_info['sentiment_indicator'].items():
            clean_dict[a_company]['sentiment_indicator'][a_date] = a_date_info['trade_info']

        counter += 1

    return clean_dict







mentioned_article_sentiment_dict = collect_article_sentiment_analysis(output_dir, collect_mentioned_articles(output_dir))
calculate_company_sentiment_stats(output_dir, mentioned_article_sentiment_dict)

