import os
import json
import logger


def rename_unit_text_as_id(task_dir, text_folder, id_key, log_filename):
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


