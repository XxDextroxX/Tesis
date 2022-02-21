import json
import os
import torch
import numpy as np
import pandas as pd

from recommender_engine.engine import RBM
from recommender_engine.vocabulary import VocabularyHelper
from recommender_engine.dataset import DatasetHelper

def train_rbm_model():
    print("Starting the training of RBM | initializing 0%")

    stored_vocab = {}
    stored_inv_vocab = {}

    # # If there is a stored vocabulary I will use it since it's more efficient
    # if os.path.exists('./data/recommender/vocabulary.json'):
    #     print("Stored vocabulary found, using it.")
    #     f = open('./data/recommender/vocabulary.json')
    #     stored_vocab = json.load(f)

    #     if os.path.exists('./data/recommender/inverse_vocabulary.json'):
    #         f = open('./data/recommender/inverse_vocabulary.json')
    #         stored_inv_vocab = json.load(f)
    #     else:
    #         print("Inverse vocabulary not found. Deleting loaded vocabulary...")
    #         stored_vocab = None

    vocabulary_helper = VocabularyHelper(stored_vocab, stored_inv_vocab)

    ### Vocabulary generetion
    print("Starting the training of RBM | processing vocab 5%")
    # If you are using a stored vocab then its indices are not gonna be lost
    data = pd.read_csv('./data_etiquetada2.csv', encoding='utf-16', sep='|')
    print(data.head(5))
    vocabulary_helper.build_vocab(custom_data=data)
    vocabulary_helper.save_vocab()
    vocab, inv_vocab = vocabulary_helper.get_vocab()

    print("Starting the training of RBM | building dataset 10%")
    dataset_helper = DatasetHelper(vocab)

    # If [from_skratch] is False then I'll be using soted values
    stored_data = torch.FloatTensor(torch.load('data/recommender/dimensional_data.pt')) \
        if os.path.exists('./data/recommender/dimensional_data.pt') else None
        

    torch_data = dataset_helper.build_dataset(
        from_skratch = True, # TODO: change it for production 
        save_data=True, 
        stored_data=stored_data,
        custom_dataset=data
    )

    nv = len(vocab) # visible nodes
    nh = 100 # hidden nodes. Not related with any data field

    print("Starting the training of RBM | training 30%")

    # Searching for stored weights
    weights = pd.read_pickle("./data/recommender/weights.pkl") \
        if os.path.exists('./data/recommender/weights.pkl') else None

    if weights is None:
        print("No weights found. Training the model from skratch")
    else:
        print("Stored weights found, using them")

    rbm = RBM(nv, nh, w = weights)

    # saving the new weights
    pd.to_pickle(rbm.w, "./data/recommender/weights.pkl")

    # fitting the machine
    rbm.fit(5, torch_data)

    # TODO: change it to be realtime
    # predicting list of words for 01.01.00
    words = rbm.predict(torch_data[0])

    print("Starting the training of RBM | done 100%")
    print("Recommended words: ")
    print(words)
    # for idx, word in enumerate(words[0][:100]):
    #     if word > 0.0:
    #         print(inv_vocab[idx])