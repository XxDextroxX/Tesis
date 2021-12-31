from numpy.core.fromnumeric import std

import pandas as pd
import numpy as np
import glob
import torch

class DatasetHelper:
    '''
    Builds and preprocess the dataset to use it in the Boltzmann Machine
    engine.
    '''
    def __init__(self):
        pass

    def build_dataset(self, from_skratch = False) -> torch.IntTensor:
        vocab = []
        raw_dataframe = self.read_dataset(all_datasets=from_skratch)

        if from_skratch:
            self.multi_data = self.__build_multidimensional_dataset(raw_dataframe, vocab)
        
        self.flat_data = self.__build_flat_dataset(self.multi_data)
        return self.flat_data

    def __build_flat_dataset(self, data: torch.IntTensor) -> torch.IntTensor:
        '''
        You should execute this method every hour in order to recalcule k and
        improve recommendations
        '''
        assert data is not None

        raw_flat = torch.subtract(data[:][:][0], data[:][:][1])
        k = self.k_generator(data)
        prob_dist = self.probability_dist_sim(raw_flat, k)
        discretized_res = self.discretize_input(prob_dist)

        return discretized_res

    def __build_multidimensional_dataset(self, data: pd.DataFrame, vocab: list) -> torch.IntTensor:
        '''
        Builds a multidimensional dataset based on a flat pandas dataframe, where rows are
        gonna be time component, columns are words (from vocabulary) and slides are the class
        of emergency or nonemergency  
        '''
        time_length = 12 * 31 * 24 # 12 months, 31 days, 24 hours
        word_length = len(vocab) # number of words in vocabulary
        classes = 2 # emergency | nonemergency
        
        # the data itself
        dataset = torch.IntTensor.new_zeros(time_length, word_length, classes)

        # going position to position in order to create the dataset
        for record in data:
            date = record['created_at'].split(' ')
            month = self.__encode_month(date[1])
            day = int(date[2]) - 1
            hour = int(date[3].split(':')[0])

            time_idx = self.__encode_time_component(month, day, hour)
            class_idx = 0 if record['class'] == 'emergencia' else 1

            for word in record['text'].split(' '):
                word_idx = self.__encode_word(word)
                dataset[time_idx][word_idx][class_idx] += 1

        return dataset

    def __encode_word(self, word) -> int:
        pass

    def __encode_time_component(self, month, day, hour) -> int:
        pass

    def __encode_month(self, month: str)->int:
        pass

    ############## Helpers ##################

    def probability_dist_sim(self, x: torch.IntTensor, k:torch.tensor = torch.tensor([1.0]))->torch.FloatTensor:
        '''
        This is the so called S(x) in created external documentation (slides).
        Simulates a probability distribution trough the sigmoid function with a [k]
        modifier so you can stretch the function as much as you need
        '''
        den_exp = -torch.divide(x, k)
        return torch.div(torch.IntTensor([1]), 1 + torch.pow(torch.e, den_exp))

    def k_generator(self, x:torch.FloatTensor) -> torch.FloatTensor:
        '''
        Generates a K value based on the proportion of frequency in the data considering
        emergency and nonemergency frequencies
        '''
        average_freq = x.mean()
        std_dev = x.std()
        len_value = len(str(int(torch.div(average_freq, std_dev))))

        return torch.pow(torch.tensor(10), torch.tensor(len_value - 1))

    def discretize_input(self, x: torch.FloatTensor, up_bound = torch.tensor([0.7]), low_bound = torch.tensor(0.4)) -> torch.IntTensor:
        '''
        Takes a probability and discretize it based on lower and upper bounds
        '''
        first_filter_1s = torch.where(x > up_bound, 1, x)
        second_filter_0s = torch.where(first_filter_1s < low_bound , 0, first_filter_1s)
        third_filter_neg1s = torch.where(second_filter_0s != 0 and second_filter_0s != 1, -1, second_filter_0s)

        return third_filter_neg1s

    def read_dataset(self, all_datasets = False)->pd.DataFrame:
        '''
        Reads the dataset (or datasets id [all_datasets] is True) and then returns it
        '''
        return self.__read_last_dataset() if not all_datasets else self.__read_all_datasets()
    
    def __read_last_dataset(self) -> pd.DataFrame:
        '''
        Reads all the generated datasets accross time and then returns it as one single
        pandas dataframe
        '''
        # The set of all the datasets of data
        dataset = pd.read_csv('data_etiquetada2.csv', sep='|', encoding='utf-16')

        # console feedback
        print(f"Loaded a dataset with [{dataset.values.shape}] records")

        return dataset

    def __read_all_datasets(self) -> pd.DataFrame:
        '''
        Reads all the generated datasets accross time and then returns it as one single
        pandas dataframe
        '''
        # All the files with this ocurrency will be loaded, so, be careful with names
        path_pattern = "*data_etiquetada2.csv"

        # store all the csv readed
        csv_datasets = [
            pd.read_csv(path,  sep='|', encoding='utf-16') \
                for path in glob.glob(path_pattern)
        ]

        # The set of all the datasets of data
        dataset = pd.concat(csv_datasets, axis=0, ignore_index=True)

        # console feedback
        print(f"Loaded a dataset with [{dataset.values.shape}] records")

        return dataset