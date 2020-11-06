import time, re, os, sys
import json
import uuid

def assign_uuid_articles(output_dir):
    article_storage_dir = output_dir + 'articles/'
    article_content_folders = os.listdir(article_storage_dir)
    article_content_folders = [i for i in article_content_folders if os.stat(article_storage_dir + i).st_size != 0]


    for an_article_date_folder in article_content_folders:
        article_list = os.listdir(article_storage_dir + an_article_date_folder)

        for an_article in article_list:
            with open(article_storage_dir + an_article_date_folder + '/' + an_article, 'r+') as article_f:
                article_json = json.load(article_f)
                article_json['article_id'] = str(uuid.uuid4())
                article_f.seek(0)
                json.dump(article_json, article_f, indent = 4)
