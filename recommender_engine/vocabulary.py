import pandas as pd
import glob

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

        # All the files with this ocurrency will be loaded, so, be careful with names
        path_pattern = "*data_etiquetada2.csv"

        # store all the csv readed
        csv_datasets = [
            pd.read_csv(path,  sep='|', encoding='utf-16') \
                for path in glob.glob(path_pattern)
        ]

        # The set of all the datasets of data
        self.dataset = pd.concat(csv_datasets, axis=0, ignore_index=True)

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