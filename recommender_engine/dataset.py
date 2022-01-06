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
    def __init__(self, vocab: dict):
        '''
        @vocab is gonna be a dict like {'perro': 0}, so I can access the index
        of the dataset throug this
        '''
        self.vocab = vocab
        self.time_encoder = {}

        index = 0
        for month in range(12):
            # Don't worry, there is no problem if all the months have
            # 31 days since if you take for example, february with 28 
            # days, the index 28, 29, and 30 will just never be accessed
            # but it raise no error, so it's ok
            for day in range(31):
                for hour in range(24):
                    self.time_encoder[f'{month}.{day}.{hour}'] = index
                    index += 1

        self.month_encoder = {
            'Jan': 0, 'Feb': 1, 'Mar': 2, 'Apr': 3, 'May': 4, 'Jun': 5, 
            'Jul': 6, 'Aug': 7, 'Sep': 8, 'Oct': 9, 'Nov': 10, 'Dec': 11
        }

    def build_dataset(self, from_skratch = False, write_data = False) -> torch.FloatTensor:
        '''
        Builds the final dataset and if @write_date is True then it will write a file
        called 'flat_data.csv', another called 'vocabulary.json', and another one called 
        'dimensional_data.npy' in this file level folder
        '''
        raw_dataframe = self.read_dataset(all_datasets=from_skratch)

        if from_skratch:
            self.multi_data = self.__build_multidimensional_dataset(raw_dataframe)
        
        self.flat_data = self.__build_flat_dataset(self.multi_data)

        if write_data:
            np.save('./dimensional_data.npy', self.multi_data.numpy())
            np.savetxt('./flat_data.csv', self.flat_data.numpy())

        return self.flat_data

    def __build_flat_dataset(self, data: torch.FloatTensor) -> torch.FloatTensor:
        '''
        You should execute this method every hour in order to recalcule k and
        improve recommendations
        '''
        assert data is not None

        # raw_flat = torch.subtract(data[:, :, 0], data[:, :, 1])
        # k = self.k_generator(data)
        prob_dist = self.probability_dist_sim(data)
        discretized_res = self.discretize_input(prob_dist)

        return discretized_res

    def __build_multidimensional_dataset(self, data: pd.DataFrame) -> torch.FloatTensor:
        '''
        Builds a multidimensional dataset based on a flat pandas dataframe, where rows are
        gonna be time component, columns are words (from vocabulary) and slides are the class
        of emergency or nonemergency  
        '''
        time_length = 12 * 31 * 24 # 12 months, 31 days, 24 hours
        word_length = len(self.vocab) # number of words in vocabulary
        classes = 2 # emergency | nonemergency
        
        # the data itself
        tensor = torch.tensor((), dtype=torch.float32)
        dataset = tensor.new_zeros((time_length, word_length, classes))

        # UPDATE THIS IF YOU CHANGE THE DATASET
        dataset_indices = {
            'created_at': 2,
            'class': -2,
            'text': 4
        }

        # going position to position in order to create the dataset
        for record in data.values:
            date = record[dataset_indices['created_at']].split(' ')
            month = self.__encode_month(date[1])
            day = int(date[2]) - 1
            hour = int(date[3].split(':')[0])

            time_idx = self.__encode_time_component(month, day, hour)
            class_idx = 0 if record[dataset_indices['class']] == 'emergencia' else 1

            for word in record[dataset_indices['text']].split(' '):
                # can't use words with a length smaller than 3 because most of the time
                # they are trash like 'ntp', 'tqm', 'no', sí', etc.
                if len(word) < 3:
                    continue
                
                word_idx = self.__encode_word(word)
                dataset[time_idx][word_idx][class_idx] += 1.0

        return dataset

    def __encode_word(self, word) -> int:
        return self.vocab[word]

    def __encode_time_component(self, month:int, day:int, hour:int) -> int:
        return self.time_encoder[f'{month}.{day}.{hour}']

    def __encode_month(self, month: str)->int:
        return self.month_encoder[month]

    ############## Helpers ##################

    def probability_dist_sim(self, x: torch.FloatTensor)->torch.FloatTensor:
        '''
        This is the so called S(x) in created external documentation (slides).
        Simulates a probability distribution trough the sigmoid function with a [k]
        modifier so you can stretch the function as much as you need
        '''
        raw_flat = torch.subtract(x[:, :, 0], x[:, :, 1])
        k = torch.abs(torch.add(x.min(dim=2).values, torch.tensor([1])))

        den_exp = -torch.divide(raw_flat, torch.FloatTensor(k))
        res = torch.div(torch.FloatTensor([1]), torch.FloatTensor([1]) + torch.pow(torch.e, den_exp))
        return res

    def k_generator(self, x:torch.FloatTensor) -> torch.FloatTensor:
        '''
        Generates a K value based on the proportion of frequency in the data considering
        emergency and nonemergency frequencies
        '''
        average_freq = x.mean()
        std_dev = x.std()
        len_value = len(str(int(torch.div(average_freq, std_dev))))

        return torch.pow(torch.tensor(10), torch.tensor(len_value - 1))

    def discretize_input(self, x: torch.FloatTensor, up_bound = torch.FloatTensor([0.7]), low_bound = torch.FloatTensor([0.4])) -> torch.FloatTensor:
        '''
        Takes a probability and discretize it based on lower and upper bounds
        '''
        # This torch works in a strange way, I mean, why the 'where' condition affects
        # all the values that doesn't match the condition????
        first_filter_1s = x.where(x < up_bound, torch.FloatTensor([1.0]))
        second_filter_0s = first_filter_1s.where(first_filter_1s > low_bound , torch.FloatTensor([0.0]))
        third_filter_neg1s = second_filter_0s.where((second_filter_0s == 0.0) | (second_filter_0s == 1.0), torch.FloatTensor([-1.0]))

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