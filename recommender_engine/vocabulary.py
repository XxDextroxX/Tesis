import json
import pandas as pd
import glob

class VocabularyHelper:
    '''
    This class will be the one that is responssible of processing the dataset
    in order to get a vocabulary. You can use an [initial_vocab] if you already
    has one, if you don't then a new one based on tweets will be created.
    '''
    def __init__(self, stored_vocab = {}, stored_inv_vocab = {}):
        '''
        Here [stored_vocab] and [stored_inv_vocab] are previous stored
        vocabularies (using save_vocabulary() method), so you can keep 
        every word index
        '''
        self.initial_vocab = None
        self.__vocab: dict = stored_vocab
        self.__inv_vocab = stored_inv_vocab

        # All the files with this ocurrency will be loaded, so, be careful with names
        path_pattern = "./data/tweets_csv/*data_etiquetada2.csv"

        # store all the csv readed
        csv_datasets = [
            pd.read_csv(path,  sep='|', encoding='utf-16') \
                for path in glob.glob(path_pattern)
        ]

        # The set of all the datasets of data
        self.dataset = pd.concat(csv_datasets, axis=0, ignore_index=True)


    def save_vocab(self):
        '''
        Saves two CSV, one for each vocabulary version (normal and inverted)
        '''
        with open('./data/recommender/vocabulary.json', 'w') as f:
            json.dump(self.__vocab, f)

        with open('./data/recommender/inverse_vocabulary.json', 'w') as f:
            json.dump(self.__inv_vocab, f)

    def get_vocab(self) -> list:
        '''
        Will Return the vocab and the inverse vocab
        '''
        if self.__vocab is {}:
            print("Error: build a vocabulary first")
            return

        return self.__vocab, self.__inv_vocab

    def build_vocab(self, custom_data=None):
        '''
        Will build a pair of vocab and inverse vocab in order to use them
        later in boltzmann engine
        '''
        # reading each single tweet in order to extract different words
        if self.initial_vocab is None:
            self.initial_vocab = set()

            # [text] is the tweet field, be aware of that
            for tweet in (custom_data['text'] if custom_data is not None else self.dataset['text']):
                # extracting only words with a lenght higher or equals than 3
                words = list(filter(lambda x: len(x) >= 3, tweet.split(' ')))
                self.initial_vocab |= set(words)

        # generating vocab based on an index
        index = len(self.__vocab)
        for _, word in enumerate(self.initial_vocab - set(self.__vocab.keys())):
            # continues the indices of the stored vocabulary
            self.__vocab[word] = index
            self.__inv_vocab[index] = word
            index += 1

        print(f"A vocabulary with {len(self.__vocab)} words has been built")