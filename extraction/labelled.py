'''
----Before to run-----
pip install gensim

'''

import pickle
import gensim
import collections


class Labelled:

    def __init__(self):
        self.loadModels()
        self.tipo = []
        self.pred_label = []

    def fill_tipo(lista: list):
        for i in range(2560):
            if i > 1279:
                lista.append(0)
            else:
                lista.append(1)
        return lista

    def loadModels(self):
        self.modelLSI = pickle.load(
            open('extraction/Modelo/ModelLSI9.model', 'rb'))
        self.DiccioLSI = pickle.load(
            open('extraction/Modelo/DiccionarioLSI9.pickle', 'rb'))
        self.MatrizSimLSI = pickle.load(
            open('extraction/Modelo/MatrizSimilaridadLSI9.pickle', 'rb'))

    def knn(self, matriz, k):
        labels = self.fill_tipo(self.tipo)
        etiquetar = []
        indice = 0
        for x in labels:
            if(indice != len(labels)-1):
                # Filtro que asigan directament 0 cuando el valor de comparacion sea 0.20 o menor
                if(matriz[indice] <= 0.20):
                    etiquetar.append((matriz[indice], 0))
                else:
                    etiquetar.append((matriz[indice], x))
            indice += 1
        etiquetar.sort(reverse=True)
        neighbors = etiquetar[:k]
        votes = []
        for neighbor in neighbors:
            votes.append(neighbor[1])
        counter = collections.Counter(votes)  # Determina el que mas se repite
        self.pred_label.append(counter.most_common()[0][0])
        return self.pred_label

    def modeloLSI(self, tweet):
        if len(tweet) <= 2:  # Se valida que el tweet preprocesado tenga un minino de palabras
            # Se le asigna el texto 'vacio' el cual sera detectado como no emergencia
            Tweet = ['vacio']
        # Se estructura el tweet en función al diccionario del modelo
        tweet_Dic = self.DiccioLSI.doc2bow(Tweet)
        # Se genera un nuevo vector que contiene el nivel de similitud del nuevo tweet con cada tweet del dataset
        sim = self.MatrizSimLSI[self.modelLSI[tweet_Dic]]
        valor_Similitud = []
        for i in range(len(sim)):
            # Se redondea cada valor del vector de similitud creado para establecer un mismo formato a todos los valores
            a = ('%.2f' % sim[i])
            valor_Similitud.append(float(a))
        return valor_Similitud


a = Labelled()
