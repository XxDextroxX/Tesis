import re, string, unicodedata
import numpy as np
import pandas as pd
import pickle
import collections

import nltk
from nltk import word_tokenize
from nltk import download
from nltk.corpus import stopwords
import csv
from random import randrange

import stanza
import gensim
download('stopwords')
download('punkt')
stanza.download('es')
nlp = stanza.Pipeline('es')
rows= []
def eliminar_textos_basura(texto):
    # eliminar emojis: elimina todo lo que este en <>. 
    texto_procesado = re.sub('<.*?>', ' ', texto)
    # convertir a minusculas
    texto_procesado = texto_procesado.lower()
    # remover @usuario
    texto_procesado = re.sub('@[^\s]+',' ',texto_procesado)
    # remover RT
    texto_procesado = re.sub('rt   ',' ',texto_procesado)
    texto_procesado = re.sub('rt',' ',texto_procesado) 
    # remover numeros
    texto_procesado = re.sub("\d+", "", texto_procesado)
    # remover barra
    texto_procesado = re.sub("|", "", texto_procesado)
    # texto_procesado = re.sub(r'http\S+', ' ', texto_procesado)
    texto_procesado = re.sub("(\w+:\/\/\S+)", " ", texto_procesado)
    # reemplazar todos los caracteres que no saen alfanuméricos con espacios
    texto_procesado = re.sub(r'[^a-zA-Z0-9ÑñÁáÉéÍíÓóÚú\s]', ' ', texto_procesado)
    return texto_procesado

def eliminar_stop_words(texto):
    # obtener lista de stopwords
    stop_words = set(stopwords.words('spanish')) 
    stop_words.remove('no')
    #separar el texto por palabras
    palabras = word_tokenize(texto) 
    # dejar solo palabras que no sean stopwords
    texto_sin_sw = [w for w in palabras if not w in stop_words] 
    #  convertir en una sola cadena la lista de palabras
    texto_sin_sw = ' '.join(texto_sin_sw)
    return texto_sin_sw 

def remove_non_ascii(word):
    """Remueve caracteres no ASCII"""
    new_word = unicodedata.normalize('NFKD', word).encode('ascii', 'ignore').decode('utf-8', 'ignore')
    return new_word

def establecer_lema(text):
  doc = nlp(text)
  new = ''
  for sent in doc.sentences:
    for word in sent.words:
      new = new + word.lemma
      new = new + ' '
  return new
  
def ProcesarTweet(Tweet):
  Procesado = eliminar_textos_basura(Tweet)
  Procesado = eliminar_stop_words(Procesado)
  Procesado = remove_non_ascii(Procesado)
  Procesado = establecer_lema(Procesado)
  return Procesado
  
def Knn(Matriz, k):
  labels = tipo
  pred_label = []
  etiquetar = []
  indice = 0
  for x in labels:
      if(indice != len(labels)-1):
        if(Matriz[indice]<=0.20): #Filtro que asigan directament 0 cuando el valor de comparacion sea 0.20 o menor 
          etiquetar.append((Matriz[indice], 0))
        else:
          etiquetar.append((Matriz[indice], x))
      indice += 1
  etiquetar.sort(reverse=True)
  neighbors = etiquetar[:k]
  votes = []
  for neighbor in neighbors:
            votes.append(neighbor[1])
  counter = collections.Counter(votes) #Determina el que mas se repite
  pred_label.append(counter.most_common()[0][0])
  return pred_label

def EtiquetaEnTexto(valor):
  if valor[0]==1:
    return 'emergencia'
  else:
    return 'no_emergencia'
    
tipo = []
for i in range(1280):
  tipo.append(1)
for j in range(1280):
  tipo.append(0)
  
modelLSI = pickle.load(open('Modelo/ModelLSI9.model','rb'))
DiccioLSI = pickle.load(open('Modelo/DiccionarioLSI9.pickle','rb'))
MatrizSimLSI = pickle.load(open('Modelo/MatrizSimilaridadLSI9.pickle','rb'))

def modeloLSI(tweet):
  Tweet = word_tokenize(ProcesarTweet(tweet)) #Se Preprocesa el tweet y se tokeniza el texto
  
  if len(Tweet) <= 2: #Se valida que el tweet preprocesado tenga un minino de palabras
    Tweet = ['vacio']  #Se le asigna el texto 'vacio' el cual sera detectado como no emergencia
  
  tweet_Dic = DiccioLSI.doc2bow(Tweet) #Se estructura el tweet en función al diccionario del modelo
  sim = MatrizSimLSI[modelLSI[tweet_Dic]] #Se genera un nuevo vector que contiene el nivel de similitud del nuevo tweet con cada tweet del dataset
  
  Valor_Similitud = [] 
  for i in range(len(sim)):
    a = ('%.2f' % sim[i]) #Se redondea cada valor del vector de similitud creado para establecer un mismo formato a todos los valores
    Valor_Similitud.append(float(a))
  
  return Valor_Similitud
  
def EtiquetarModelLSI(tweet):
  Similaridad= modeloLSI(tweet)
  k_5 = Knn(Similaridad, 5)
  return k_5 

from datetime import datetime
import datetime as dtt
import time
import tweepy as tw
import json
from tweepy import OAuthHandler
import csv   
import pytz





api_key = 's2Z3bF6BkBBm0gJHmEVF36UQI'
api_secret = 'GUc9EAG2pzUMaHbbAaJFoenDmOkZ7wsBROR377K4LkzaJBsFmx'
access_token = '844685305944965125-zqj5vYiYyEQUUxftoYhDRDhMnDljqaY'
access_secret = 'Vs3Jz8eLIq4FT8vGVhGsxtchjmT789dTFFYFHQ9pFiqkJ'
auth = OAuthHandler(api_key, api_secret)
auth.set_access_token(access_token, access_secret)

api = tw.API(auth, wait_on_rate_limit=True)

#--removido: segundos=16
#--removido: desde=datetime.today()
#--removido: desde=desde-dtt.timedelta(seconds=segundos)
#--removido: fechita=desde
#--removido: desde=str(desde.date())
places = api.geo_search(query='Ecuador', granularity="country")
place_id = places[0].id



#Inicialización de la función de randomizado bajo probabilidades para listas

def switch_demo():
    switcher = {
        range(0, 47): 1, #0-46 = lista 1
        range(47, 58): 2,#47-57 = lista 2
        range(58, 69): 3,#...
        range(69, 80): 4,#...
        range(80, 82): 5,#...
        range(82, 84): 6,#...
        range(84, 86): 7,#...
        range(86, 88): 8,#...
        range(88, 90): 9,#...
        range(90, 92): 10,#...
        range(92, 94): 11,#...
        range(94, 96): 12,#...
        range(96, 98): 13,#...
        range(98, 100): 14#98-99 = Lista
    }
    argument=randrange(100)
    for key in switcher:
        if argument in key:
            return switcher[key]
    return 1



global documento
try:
    documento=pd.read_csv('data_streaming.csv',  delimiter='|')
except:
  with open('data_streaming.csv', 'a') as f:
            writer = csv.writer(f, delimiter='|')
            writer.writerow(['user_id', 'status_id', 'created_at', 'screen_name', 'text',
            'status_url', 'lat',
            'long', 'place_full_name','revisado'])
#Código para comprobar si existe Resultados
try:
    Docu=pd.read_csv('data_etiquetada.csv', delimiter='|')
except:
  with open('data_etiquetada.csv', 'a') as f:
            writer = csv.writer(f, delimiter='|')
            writer.writerow(['user_id', 'status_id', 'created_at', 'screen_name', 'text',
            'status_url','lat',
            'long', 'place_full_name', 'class', 'institution'])


if 'ids' in globals():
  print('Directo a captura')
else:
  documento=pd.read_csv('data_streaming.csv', delimiter='|')
  global ids
  ids=documento['status_id'].values.tolist()