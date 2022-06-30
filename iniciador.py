"""
This file will be deleted in the future...
"""
import pickle
import collections
# from joblib import dump
from joblib import load

rows = []


def Knn(Matriz, k):
    labels = tipo
    pred_label = []
    etiquetar = []
    indice = 0
    for x in labels:
        if(indice != len(labels)-1):
            # Filtro que asigan directament 0 cuando el valor de comparacion sea 0.20 o menor
            if(Matriz[indice] <= 0.20):
                etiquetar.append((Matriz[indice], 0))
            else:
                etiquetar.append((Matriz[indice], x))
        indice += 1
    etiquetar.sort(reverse=True)
    neighbors = etiquetar[:k]
    votes = []
    for neighbor in neighbors:
        votes.append(neighbor[1])
    counter = collections.Counter(votes)  # Determina el que mas se repite
    pred_label.append(counter.most_common()[0][0])
    return pred_label


def EtiquetaEnTexto(valor):
    if valor[0] == 1:
        return 'emergencia'
    else:
        return 'no_emergencia'


tipo = []
for i in range(1280):
    tipo.append(1)
for j in range(1280):
    tipo.append(0)

modelLSI = pickle.load(open('Tesis/Modelo/ModelLSI9.model', 'rb'))
DiccioLSI = pickle.load(open('Tesis/Modelo/DiccionarioLSI9.pickle', 'rb'))
MatrizSimLSI = pickle.load(
    open('Tesis/Modelo/MatrizSimilaridadLSI9.pickle', 'rb'))


def modeloLSI(tweet):
    # Tweet = word_tokenize(ProcesarTweet(tweet)) #Se Preprocesa el tweet y se tokeniza el texto

    if len(tweet) <= 2:  # Se valida que el tweet preprocesado tenga un minino de palabras
        # Se le asigna el texto 'vacio' el cual sera detectado como no emergencia
        tweet = ['vacio']

    # Se estructura el tweet en función al diccionario del modelo
    tweet_Dic = DiccioLSI.doc2bow(tweet)
    # Se genera un nuevo vector que contiene el nivel de similitud del nuevo tweet con cada tweet del dataset
    sim = MatrizSimLSI[modelLSI[tweet_Dic]]

    Valor_Similitud = []
    for i in range(len(sim)):
        # Se redondea cada valor del vector de similitud creado para establecer un mismo formato a todos los valores
        a = ('%.2f' % sim[i])
        Valor_Similitud.append(float(a))

    return Valor_Similitud


def EtiquetarModelLSI(tweet):
    Similaridad = modeloLSI(tweet)
    k_5 = Knn(Similaridad, 5)
    return k_5


# classifier_bi = load('Tesis/Modelo/classifier_bi.joblib')
# classifier_mul = load('Tesis/Modelo/classifier_mul.joblib')
# real_vectorizer_bi = load('Tesis/Modelo/real_vectorizer_bi.joblib')
# real_vectorizer_mul = load('Tesis/Modelo/real_vectorizer_mul.joblib')


def make_prediction(text):
    MatrizSimLSI = pickle.load(
        open('Tesis/Modelo/cl_bi_prueba.pickle', 'rb'))
    print(MatrizSimLSI)
    # with open("Tesis/Modelo/vector_bi_prueba.pickle", "rb") as f:
    #     vector_bi_prueba = pickle.load(f)

    # with open("Tesis/Modelo/cl_bi_prueba.pickle", "rb") as f:
    #     cl_bi_prueba = pickle.load(f)

    # with open("Tesis/Modelo/vector_mul_prueba.pickle", "rb") as f:
    #     vector_mul_prueba = pickle.load(f)

    # with open("Tesis/Modelo/cl_mul_prueba.pickle", "rb") as f:
    #     cl_mul_prueba = pickle.load(f)

    # vector_text_bi = vector_bi_prueba.transform([text])
    # predict_bi = cl_bi_prueba.predict(vector_text_bi)
    # if predict_bi[0] == 'emergencia':
    #     vector_text_mul = vector_mul_prueba.transform([text])
    #     predict_mul = cl_mul_prueba.predict(vector_text_mul)
    #     return predict_bi[0], predict_mul[0]
    # else:
    #     return predict_bi[0], "no_emergencia"


make_prediction('Anoche tenia frio y hambre por que tu estabas bien fea')
