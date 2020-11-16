import nltk
# nltk.download()
# nltk.download('wordnet')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('stopwords')

import time, re, os, sys
import itertools, collections
import string
import json
import operator
import pandas as pd
import numpy as np


from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk import FreqDist
from nltk.corpus import words

# https://www.wsj.com/articles/SB10001424052970203550304577139043766630090
# content = "NEW YORK\u2014A judge in New York state court delivered a ruling in favor of mortgage-bond insurers in a case over mortgage-backed securities Countrywide Financial had insured by\n\n\n\n\n\n\n            MBIA Inc.\n\n        MBI 1.72%\n\n\nIn the ruling, highly anticipated among banks and bond insurers, New York Supreme Court Justice Eileen Bransten said MBIA doesn't have to prove direct correlation between allegedly fraudulent statements made by Countrywide and the souring of the mortgage bonds. That could make MBIA's arguments easier to prove, and potentially deals a significant blow to Countrywide's defense.\n\n\n\nHeard on the Street  BofA's Destiny Still Lies in the Courts \n\n\n\n\n\n\nMBIA is suing Countrywide, now owned by\n\n\n\n\n\n\n            Bank of America Corp.\n\n        BAC 1.16%\n\n\n      , for fraud in having it insure the mortgage bonds, which imploded when the housing bubble burst. \"We are very pleased by today's ruling,\" MBIA Chief Executive Jay Brown said. \"The ruling provides us with a straightforward path to recovery of our losses.\"\nStill, Bank of America also won part of the ruling, as Judge Bransten denied the attempt by the insurer to get a ruling that would have allowed it to pursue claims against even performing mortgage bonds. \n\n\nAnd MBIA still must prove that any allegedly fraudulent statements Countrywide made actually induced it to sign the insurance agreement, likely still a difficult task. The ruling could also still be appealed.\nA Bank of America spokesman said the bank is still reviewing the \"complex\" decision, but said the judge denied key parts of MBIA's motions. \n\"The insurer's losses are due to the mortgage-market collapse, a risk they agreed to insure,\" the spokesman said. \"MBIA still must prove that it was damaged by Countrywide's allegedly material misrepresentation, which as the court stated 'will not be an easy task.'\" \nMBIA leapt 94 cents, or 8.1%, to $12.53 in 4 p.m. New York Stock Exchange trading, spiking just before the close; its shares continued to rise in after-hours trading. Bank of America ended up 24 cents, or 4.3%, at $5.80, also on the Big Board, pulling back after rising as high as $5.88 late in the session. \nBank of America has argued any errors in underwriting didn't cause the borrowers to default on their loans, and thereby didn't affect investors or insurers of mortgage bonds. \nWhile the ruling may contradict that, it won't necessarily set a precedent for rulings in other courts. It is likely, however, that MBIA will cite it in other cases, according to a person familiar with the matter. \nMortgage-bond insurers suffered heavily after the mortgage bubble burst and caused widespread default in the bonds. Many have filed suits against the biggest sellers of mortgage-backed securities, hoping to reclaim some lost funds. \nFor MBIA, the ruling will spark new hopes it will be able to recover losses from Countrywide, possibly in a settlement. MBIA had earlier in this case won another ruling that the insurer could use statistical sampling to help it prove its case. \nMBIA last month reached a settlement with\n\n\n\n\n\n\n            Morgan Stanley\n\n        MS 1.91%\n\n\n      over various claims and counterclaims between the two sides, including the allegation from the insurer that the investment bank misrepresented tens of millions of dollars worth of mortgages backing the loans.\nBank of America, as had Morgan Stanley, sued MBIA over the insurer's plan to split its businesses. Morgan Stanley agreed to drop those claims in its settlement and MBIA has previously said it is in discussions with all parties in that case.\n\nCopyright \u00a92020 Dow Jones & Company, Inc. All Rights Reserved. 87990cbe856818d5eddac44c7b1cdeb8"
# print(word_tokenize(content))

# https://www.digitalocean.com/community/tutorials/how-to-perform-sentiment-analysis-in-python-3-using-the-natural-language-toolkit-nltk
def lemmatize_sentence(tokens):
    lemmatizer = WordNetLemmatizer()
    lemmatized_sentence = []
    for word, tag in pos_tag(tokens):
        if tag.startswith('NN'):
            pos = 'n'
        elif tag.startswith('VB'):
            pos = 'v'
        else:
            pos = 'a'
        lemmatized_sentence.append(lemmatizer.lemmatize(word, pos))
    return lemmatized_sentence

def remove_noise(tweet_tokens, stop_words = stopwords.words('english'), min_token_len = 1, max_token_len = 30):
    cleaned_tokens = []
    for token, tag in pos_tag(tweet_tokens):
        token = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|'\
                       '(?:%[0-9a-fA-F][0-9a-fA-F]))+','', token)
        token = re.sub("(@[A-Za-z0-9_]+)","", token)

        if tag.startswith("NN"):
            pos = 'n'
        elif tag.startswith('VB'):
            pos = 'v'
        else:
            pos = 'a'

        lemmatizer = WordNetLemmatizer()
        token = lemmatizer.lemmatize(token, pos)
        if len(token) > min_token_len and len(token) <= max_token_len and token not in string.punctuation and token.lower() not in stop_words and token.lower() in words.words():
            cleaned_tokens.append(token.lower())
    return cleaned_tokens

####################################################################################################

def get_most_freq_words(content, most_common_thld = 100):
    tokenized_content = word_tokenize(content)
    lemmatized_token = lemmatize_sentence(tokenized_content)
    cleaned_token = remove_noise(lemmatized_token)
    freq_dist_pos = FreqDist(cleaned_token)
    return freq_dist_pos.most_common(most_common_thld)

def get_sentiment_word_dict():
    sentiment_word_list_dir = './data_cleaner/Loughran_McDonald_sentiment_word_lists.xlsx'
    sheet_name_list = ['Negative', 'Positive', 'Uncertainty', 'Litigious', 'StrongModal', 'WeakModal', 'Constraining']

    sentiment_word_dict = dict()
    for a_sheet in sheet_name_list:
        temp_df = pd.read_excel(sentiment_word_list_dir, sheet_name=a_sheet, header=None)
        temp_list = temp_df[temp_df.columns[0]].tolist()
        temp_list = [i.lower() for i in temp_list]
        sentiment_word_dict[a_sheet.lower()] = temp_list
    return sentiment_word_dict



def get_sentiment_analysis(content, sentiment_word_dict = get_sentiment_word_dict(), most_common_thld = 100):
    clean_token = get_most_freq_words(content, most_common_thld = most_common_thld)

    sentiment_analysis_dict = {k: 0 for k in sentiment_word_dict.keys()}

    for a_word, a_word_freq in clean_token:
        for a_catagory, a_catagory_word_list in sentiment_word_dict.items():
            if a_word in a_catagory_word_list:
                sentiment_analysis_dict[a_catagory] += a_word_freq

    return sentiment_analysis_dict


# print(get_sentiment_analysis(content))
