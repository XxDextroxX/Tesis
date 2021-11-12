
'''
------------install before start-------------
pip install stanza
pip install emoji
pip install nltk
pip install pandas

'''
import stanza  # helps to lemmatize and tokenize words
import nltk  # NLP tools
import datetime  # helps to format dates
import re  # regular expression support
import unicodedata
from urllib.parse import unquote  # this: unquote('abc%20def') -> 'abc def'
# Keep emoji sense but remove its unicode value => :( -> :sad:
from emoji import demojize
from nltk.corpus import stopwords
from nltk import word_tokenize  # stanza can tokenize as well, but this lighter
from string import punctuation

import tqdm  # It's to stream data in order to create progress bars
# import tensorflow as tf
# from tensorflow.keras import layers

import random


class Preprocessing:

    def __init__(self):
        self.stanza_pipeline = stanza.Pipeline(
            lang='es', processors='tokenize,mwt,pos,lemma')
        self.stopwords_ = set(stopwords.words("spanish"))
        self.stopwords_.remove('no')

    def download():
        nltk.download('stopwords')
        nltk.download('punkt')
        nltk.download('wordnet')
        stanza.download('es')

    def clean_text(self, text):
        text = text.lower()  # Lowercase text
        text = re.sub('@[^\s]+', ' ', text)  # removing @user
        text = re.sub('rt', ' ', text)  # removing retweet tag
        text = re.sub(f"[{re.escape(punctuation)}]",
                      "", text)  # Remove punctuation
        text = re.sub(r'http\S+', '', text)  # remove hyperlinks
        text = re.sub(r'#\S+', '', text)
        text = re.sub(r'@\S+', '', text)
        # remove HTML tags but keep their content
        text = re.sub(r"<.*?>", " ", text)
        text = re.sub(r"\b[0-9]+\b\s*", "", text)  # removing numbers from text
        # removing all non alphabet characters
        text = re.sub(r"[^A-Za-z\s]+", "", text)
        # Remove extra spaces, tabs, and new lines
        text = " ".join(text.split())
        return text

    # 'NO' is allowed as a stopword

    def remove_stopwords(self, text):
        tokens = word_tokenize(text, language="spanish")
        clean_tokens = [t for t in tokens if not t in self.stopwords_]
        clean_text = " ".join(clean_tokens)
        return clean_text

    def changeLyrics(self, text):
        trans_tab = dict.fromkeys(map(ord, u'\u0301\u0308'), None)
        text = unicodedata.normalize(
            'NFKC', unicodedata.normalize('NFKD', text).translate(trans_tab))
        return text

    def lemmatize_text(self, text):
        doc = self.stanza_pipeline(text)
        lista_lematizada = ''
        for sent in doc.sentences:
            for word in sent.words:
                lista_lematizada = lista_lematizada + word.lemma
                lista_lematizada = lista_lematizada + ' '
        return lista_lematizada

    def clean_data(self, text):
        text = self.changeLyrics(text)
        text = self.lemmatize_text(text)
        text = self.clean_text(text)
        text = self.remove_stopwords(text)
        # text = demojize(text, language='es')
        return text
