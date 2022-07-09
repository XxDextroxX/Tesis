import pandas as pd
import string
from sklearn import metrics
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score, f1_score, classification_report
import pickle
# import Preprocessing


class TrainModel:
    def __init__(self):
        self.path_data_bi = '../dataset/data_bi.csv'
        self.path_data_mul = '../dataset/data_mul.csv'
        self.path_real_vectorizer_bi = '../Modelo/real_vectorizer_bi.pickle'
        self.path_classifier_bi = '../Modelo/classifier_bi.pickle'
        self.path_real_vectorizer_mul = '../Modelo/real_vectorizer_mul.pickle'
        self.path_classifier_mul = '../Modelo/classifier_mul.pickle'
        # self.main()
        # self.real_vectorizer_bi, self.classifier_bi, self.real_vectorizer_mul, self.classifier_mul = self.load_models()

    def load_dataset_bi(self):
        self.data = pd.read_csv(self.path_data_bi, encoding='utf-16')
        return self.data

    def load_dataset_mul(self):
        self.data = pd.read_csv(self.path_data_mul, encoding='utf-16')
        return self.data

    def tokenize(self, sentence):
        punctuation = set(string.punctuation)
        tokens = []
        for token in sentence.split():
            new_token = []
            for character in token:
                if character not in punctuation:
                    new_token.append(character.lower())
            if new_token:
                tokens.append("".join(new_token))
        return tokens

    def make_model_bi(self):
        self.classifier_bi = LinearSVC()
        return self.classifier_bi

    def make_model_mul(self):
        self.classifier_mul = LinearSVC()
        return self.classifier_mul

    def train_test_divide(self, data, X, Y):
        self.a, self.b, self.c, self.d = train_test_split(
            data[X], data[Y], stratify=data[Y], random_state=1)
        print(
            f"Training examples: {len(self.a)}, testing examples {len(self.b)}")
        return self.a, self.b, self.c, self.d

    def transform_vector(self, tokenize, train_text, test_text):
        self.real_vectorizer = CountVectorizer(
            tokenizer=tokenize, binary=True)
        self.train_X = self.real_vectorizer.fit_transform(train_text)
        self.test_X = self.real_vectorizer.transform(test_text)
        return self.train_X, self.test_X, self.real_vectorizer

    def fit_model_bi(self):
        print('Staring train model binary')
        self.data_bi = self.load_dataset_bi()
        self.train_text_bi, self.test_text_bi, self.train_labels_bi, self.test_labels_bi = self.train_test_divide(
            self.data_bi, 'text', 'class')
        self.train_X_bi, self.test_X_bi, self.real_vectorizer_bi = self.transform_vector(
            self.tokenize, self.train_text_bi, self.test_text_bi)
        self.classifier_bi = self.make_model_bi()
        self.classifier_bi.fit(self.train_X_bi, self.train_labels_bi)
        self.y_pred = self.classifier_bi.predict(self.test_X_bi)
        self._classification_report = classification_report(
            self.test_labels_bi, self.y_pred, digits=3)
        print(self._classification_report)
        print('Accuracy: %.4f' % accuracy_score(
            self.test_labels_bi, self.y_pred))
        print('End train model binary')
        return self.real_vectorizer_bi, self.classifier_bi

    def fit_model_mul(self):
        print('Staring train model multi-class')
        self.data_mul = self.load_dataset_mul()
        self.train_text_mul, self.test_text_mul, self.train_labels_mul, self.test_labels_mul = self.train_test_divide(
            self.data_mul, 'text', 'category')
        self.train_X_mul, self.test_X_mul, self.real_vectorizer_mul = self.transform_vector(
            self.tokenize, self.train_text_mul, self.test_text_mul)
        self.classifier_mul = self.make_model_mul()
        self.classifier_mul.fit(self.train_X_mul, self.train_labels_mul)
        self.y_pred = self.classifier_mul.predict(self.test_X_mul)
        self._classification_report = classification_report(
            self.test_labels_mul, self.y_pred, digits=3)
        print(self._classification_report)
        print('Accuracy: %.4f' % accuracy_score(
            self.test_labels_mul, self.y_pred))
        print('End train model multi-class')
        return self.real_vectorizer_mul, self.classifier_mul

    def save_pickle(self, name, obj):
        print('--------------------------------------')
        print('Save pickle')
        with open(f'../Modelo/{name}.pickle', "wb") as f:
            pickle.dump(obj, f)
            f.close()
        print('pickle create with exists')
        print('--------------------------------------')

    def main(self):
        self.real_vectorizer_bi, self.classifier_bi = self.fit_model_bi()
        self.save_pickle('real_vectorizer_bi', self.real_vectorizer_bi)
        self.save_pickle('classifier_bi', self.classifier_bi)
        self.real_vectorizer_mul, self.classifier_mul = self.fit_model_mul()
        self.save_pickle('real_vectorizer_mul', self.real_vectorizer_mul)
        self.save_pickle('classifier_mul', self.classifier_mul)

    def load_models(self):
        print('Loading models')
        with open(self.path_real_vectorizer_bi, "rb") as f:
            self.real_vectorizer_bi = pickle.load(f)
            f.close()
        with open(self.path_classifier_bi, "rb") as f:
            self.classifier_bi = pickle.load(f)
            f.close()
        with open(self.path_real_vectorizer_mul, "rb") as f:
            self.real_vectorizer_mul = pickle.load(f)
            f.close()
        with open(self.path_classifier_mul, "rb") as f:
            self.classifier_mul = pickle.load(f)
            f.close()
        print('Process finish with exists')
        return self.real_vectorizer_bi, self.classifier_bi, self.real_vectorizer_mul, self.classifier_mul

    # def make_prediction(self, text):
    #     vector_text_bi = self.real_vectorizer_bi.transform([text])
    #     predict_bi = self.classifier_bi.predict(vector_text_bi)
    #     if predict_bi[0] == 'emergencia':
    #         vector_text_mul = self.real_vectorizer_mul.transform([text])
    #         predict_mul = self.classifier_mul.predict(vector_text_mul)
    #         return predict_bi[0], predict_mul[0]
    #     else:
    #         return predict_bi[0], "no_emergencia"

    def make_prediction(self, text, real_vectorizer_bi, classifier_bi, real_vectorizer_mul, classifier_mul):
        vector_text_bi = real_vectorizer_bi.transform([text])
        predict_bi = classifier_bi.predict(vector_text_bi)
        if predict_bi[0] == 'emergencia':
            vector_text_mul = real_vectorizer_mul.transform([text])
            predict_mul = classifier_mul.predict(vector_text_mul)
            return predict_bi[0], predict_mul[0]
        else:
            return predict_bi[0], "no_emergencia"


# TrainModel()
