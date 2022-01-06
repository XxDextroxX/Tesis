import pandas as pd
import os

from recommender_engine.engine import RBM
from recommender_engine.vocabulary import VocabularyHelper
from recommender_engine.dataset import DatasetHelper

def train_rbm_model():
    print("Starting the training of RBM | initializing 0%")
    vocabulary_helper = VocabularyHelper()

    ### Vocabulary generetion
    print("Starting the training of RBM | processing vocab 5%")
    vocabulary_helper.build_vocab()
    vocab, inv_vocab = vocabulary_helper.get_vocab()

    print("Starting the training of RBM | building dataset 10%")
    dataset_helper = DatasetHelper(vocab)
    torch_data = dataset_helper.build_dataset(from_skratch = True, write_data=True)

    nv = len(vocab) # visible nodes
    nh = 100 # hidden nodes. Not related with any data field

    print("Starting the training of RBM | training 30%")

    # Searching for stored weights
    weights = pd.read_pickle("./weights.pkl") if os.path.exists('./weights.pkl') else None

    if weights is None:
        print("No weights found. Training the model from skratch")
    else:
        print("Stored weights found. Using stored weights.")

    rbm = RBM(nv, nh, w = weights)

    # saving the new weights
    pd.to_pickle(rbm.w, "./weights.pkl")

    # fitting the machine
    rbm.fit(100, torch_data)

    # TODO: change it to be realtime
    # predicting list of words for 01.01.00
    words = rbm.predict(torch_data[0])

    print("Starting the training of RBM | done 100%")
    print("Recommended words: ")
    print(words)
    # for idx, word in enumerate(words[0][:100]):
    #     if word > 0.0:
    #         print(inv_vocab[idx])