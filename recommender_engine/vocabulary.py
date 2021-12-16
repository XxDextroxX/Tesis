import pandas as pd

class VocabularyHelper:
    '''
    This class will be the one that is responssible of processing the dataset
    in order to get a vocabulary. You can use an [initial_vocab] if you already
    has one, if you don't then a new one based on tweets will be created.
    '''
    def __init__(self, initial_vocab: set = None):
        self.initial_vocab = initial_vocab
        self.__vocab = {}
        self.__inv_vocab = {}
        self.dataset = pd.read_csv('data_streaming_preprocessing.csv', sep='|', encoding='utf-16')

    def get_vocab(self) -> list:
        '''
        Will Return the vocab and the inverse vocab
        '''
        if self.__vocab is {}:
            print("Error: build a vocabulary first")
            return

        return self.__vocab, self.__inv_vocab

    def build_vocab(self):
        '''
        Will build a pair of vocab and inverse vocab in order to use them
        later in boltzmann engine
        '''
        # reading each single tweet in order to extract different words
        if self.initial_vocab is None:
            self.initial_vocab = set()

            # [text] is the tweet field, be aware of that
            for tweet in self.dataset['text']:
                # extracting only words with a lenght higher or equals than 3
                words = list(filter(lambda x: len(x) >= 3, tweet.split(' ')))
                self.initial_vocab |= set(words)

        # generating vocab based on an index
        for idx, word in enumerate(self.initial_vocab):
            self.__vocab[word] = idx
            self.__inv_vocab[idx] = word