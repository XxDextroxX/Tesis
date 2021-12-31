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
    

    ############## Helpers ##################

    def probability_dist_sim(self, x: torch.tensor, k:float = 1.0):
        '''
        This is the so called S(x) in created external documentation (slides).
        Simulates a probability distribution trough the sigmoid function with a [k]
        modifier so you can stretch the function as much as you need
        '''
        den_exp = -torch.divide(x, k)
        return torch.div(torch.tensor([1]), 1 + torch.pow(torch.e, den_exp))

    def k_generator(self, x:torch.tensor) -> float:
        average_freq = x.mean()

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