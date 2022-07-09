import stanza  # helps to lemmatize and tokenize words
import nltk  # NLP tools
import re  # regular expression support
import unicodedata
# Keep emoji sense but remove its unicode value => :( -> :sad:
from emoji import demojize
from nltk.corpus import stopwords
from nltk import word_tokenize  # stanza can tokenize as well, but this lighter
# from string import punctuation
import pandas as pd
from sklearn.utils import resample


class Preprocessing:

    def __init__(self):

        self.stanza_pipeline = stanza.Pipeline(
            lang='es', processors='tokenize,mwt,pos,lemma')
        self.stopwords_ = set(stopwords.words("spanish"))
        self.stopwords_.remove('no')

    # This is static and should be excecuted once
    def download():
        nltk.download('stopwords')
        nltk.download('punkt')
        nltk.download('wordnet')
        stanza.download('es')

    def clean_text(self, text):
        text = text.lower()  # Lowercase text
        text = re.sub('@[^\s]+', ' ', text)  # removing @user
        # text = re.sub('rt', ' ', text) # removing retweet tag
        # text = re.sub(f"[{re.escape(punctuation)}]", "", text)  # Remove punctuation
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

    def remove_stopwords(self, text):
        tokens = word_tokenize(text, language="spanish")
        clean_tokens = [t for t in tokens if not t in self.stopwords_]
        clean_text = " ".join(clean_tokens)
        return clean_text

    # This will handle accents
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
        return text

    def clean_data_train(self, data):
        data["text"] = data["text"].apply(self.changeLyrics)
        data["text"] = data["text"].apply(self.clean_text)
        data["text"] = data["text"].apply(self.remove_stopwords)

    def create_data_bi(self, data):
        self.aux = data
        self.clean_data_train(self.aux)
        self.class_emergencia = self.aux[self.aux['class'] == 'emergencia']
        self.class_no_emergencia = self.aux[self.aux['class']
                                            == 'no_emergencia']
        self.reesampled_data = resample(
            self.class_emergencia,
            replace=True,
            n_samples=self.class_no_emergencia.shape[0],
            random_state=0
        )
        print('Data balanced with exits')
        data_bi = pd.concat([self.class_no_emergencia, self.reesampled_data])
        print(data_bi['class'].value_counts())
        return data_bi

    def create_data_mul(self, data):
        self.aux = data
        self.clean_data_train(self.aux)
        self.data_emergency = self.aux[self.aux['class'] == 'emergencia']
        self.class_1 = self.data_emergency[self.data_emergency['category']
                                           == 'transito_movilidad']
        self.class_2 = self.data_emergency[self.data_emergency['category']
                                           == 'gestion_riesgos']
        self.class_3 = self.data_emergency[self.data_emergency['category']
                                           == 'seguridad_ciudadana']
        self.class_4 = self.data_emergency[self.data_emergency['category']
                                           == 'servicios_municipales']
        self.class_5 = self.data_emergency[self.data_emergency['category']
                                           == 'gestion_sanitaria']
        self.n = max(len(self.class_1), len(self.class_2), len(
            self.class_3), len(self.class_4), len(self.class_5))
        self.reesampled_data_1 = resample(
            self.class_2,
            replace=True,
            n_samples=self.n,
            random_state=0
        )

        self.reesampled_data_2 = resample(
            self.class_3,
            replace=True,
            n_samples=self.n,
            random_state=0
        )

        self.reesampled_data_3 = resample(
            self.class_4,
            replace=True,
            n_samples=self.n,
            random_state=0
        )

        self.reesampled_data_4 = resample(
            self.class_5,
            replace=True,
            n_samples=self.n,
            random_state=0
        )
        self.data_emergency = pd.concat([self.class_1, self.reesampled_data_1,
                                         self.reesampled_data_2, self.reesampled_data_3, self.reesampled_data_4], axis=0)
        print('data balanced with exists')
        print(self.data_emergency['category'].value_counts())
        self.data_emergency = self.data_emergency[pd.notnull(
            self.data_emergency['category'])]
        return self.data_emergency
