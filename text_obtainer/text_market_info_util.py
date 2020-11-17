import os
import json
import logger


def rename_unit_text_as_id(task_dir, text_folder = 'articles', id_key = 'article_id', log_filename = 'WSJ_text_market_util_log'):
    logger_dir = task_dir + 'logs/'
    log_filename = log_filename + '.txt'

    article_storage_dir = task_dir + text_folder + '/'
    article_content_folders = os.listdir(article_storage_dir)
    article_content_folders = [i for i in article_content_folders if os.stat(article_storage_dir + i).st_size != 0]

    for an_article_date_folder in article_content_folders:
        article_list = os.listdir(article_storage_dir + an_article_date_folder)

        for an_article in article_list:
            article_full_dir = article_storage_dir + an_article_date_folder + '/'
            article_file_path_o = article_full_dir + an_article
            try:
                with open(article_file_path_o, 'r') as article_f:
                    article_json = json.load(article_f)
                    article_file_name_n = article_json[id_key]
            except KeyError as e:
                error_msg = f"{article_file_path_o} failed to change filename to '{id_key}' due to {e}."
                logger.register_log(error_msg, logger_dir, log_filename)
                continue
            article_file_path_n = article_full_dir + article_file_name_n + '.json'

            os.rename(str(article_file_path_o), str(article_file_path_n))
            log_msg = f"{article_file_path_o} successfully renamed as '{article_file_name_n}'."
            logger.register_log(log_msg, logger_dir, log_filename)


def replace_quote_with_market_data_LUT_info(task_dir, text_folder = 'articles', market_data_folder = 'market_data', LUT_filename = 'company_market_LUT', LUT_quote_key = 'quoted_in', log_filename = 'WSJ_text_market_util_log'):
    logger_dir = task_dir + 'logs/'
    log_filename = log_filename + '.txt'

    article_full_path_dict = dict()
    article_storage_dir = task_dir + text_folder + '/'
    article_content_folders = os.listdir(article_storage_dir)
    article_content_folders = [i for i in article_content_folders if os.stat(article_storage_dir + i).st_size != 0]
    for an_article_date_folder in article_content_folders:
        article_list = os.listdir(article_storage_dir + an_article_date_folder)
        for an_article in article_list:
            an_article_full_path = article_storage_dir + an_article_date_folder + '/' + an_article
            an_article = an_article.split('.')[0]
            article_full_path_dict[an_article] = an_article_full_path
            with open(an_article_full_path, 'r') as article_f_o:
                article_json = json.load(article_f_o)
                article_json['quotes'] = []
            with open(an_article_full_path, 'w+') as article_f_n:
                json.dump(article_json, article_f_n, indent = 4)


    LUT_dir = task_dir + market_data_folder + '/' + LUT_filename + '.json'
    with open(LUT_dir, 'r') as LUT_f:
        LUT_data = json.load(LUT_f)

    for k, v in LUT_data.items():
        if len(v[LUT_quote_key]) != 0:
            for an_article_id in v[LUT_quote_key]:
                try:
                    an_article_full_path = article_full_path_dict[an_article_id]
                except KeyError as e:
                    error_msg = f"{an_article_id} under {k} failed to retrieve full path from article_full_path_dict."
                    logger.register_log(error_msg, logger_dir, log_filename)
                    continue

                with open(an_article_full_path, 'r') as article_f_o:
                    article_json = json.load(article_f_o)
                    article_json['quotes'] = article_json['quotes'] + [str(k)]
                with open(an_article_full_path, 'w+') as article_f_n:
                    json.dump(article_json, article_f_n, indent = 4)

                log_msg = f"{an_article_full_path} successfully updated with {k} as quotes."
                logger.register_log(log_msg, logger_dir, log_filename)



