import pandas as pd
import numpy as np
import torch

class DatasetHelper:
    '''
    Builds and preprocess the dataset to use it in the Boltzmann Machine
    engine.
    '''
    def __init__(self, path):
        self.target_attr = ['created_at', 'text']
        self.stored_dataset = None
        self.dataset = pd.read_csv(path, sep='|', encoding='utf-16')
        self.month_encoder = {
            'Jan': 0,
            'Feb': 1,
            'Mar': 2,
            'Apr': 3,
            'May': 4,
            'Jun': 5,
            'Jul': 6,
            'Aug': 7,
            'Sep': 8,
            'Oct': 9,
            'Nov': 10,
            'Dec': 11
        }

    def build_dataset(self)->pd.DataFrame:
        '''
        Builds a dataset with time features processed. If you wann use this as an input to
        the torch library you should call the [trasform] method after this.
        '''
        #  This are the attributes I wanna explore in RBMs
        raw_filtered_data = self.dataset.loc[:, self.target_attr]

        day = []
        month = []
        
        # filling up the time component
        for date in raw_filtered_data['created_at'].values:
            month_, day_ = date.split(' ')[1:3]
            month.append(month_)
            day.append(day_)
        
        # Creating a new dataframe to stack with the previous one
        date_pd = pd.DataFrame(np.vstack([day, month]).T, columns=["day", "month"])
        column_names = np.hstack([raw_filtered_data.columns.values, date_pd.columns.values])

        # Adding new time features to the original dataset
        raw_filtered_data = pd.concat([raw_filtered_data, date_pd], ignore_index=True, axis=1)

        raw_filtered_data.columns = column_names

        # This [created_at] is not useful anymore since we're using the new [date_pd]
        # features
        raw_filtered_data = raw_filtered_data.drop(['created_at'], axis=1)
        raw_filtered_data['month'] = raw_filtered_data['month'].apply(lambda x: self.month_encoder[x])

        self.stored_dataset = raw_filtered_data
        return self.stored_dataset

    def transform_torch(self, vocab_dict):
        '''
        Transforms the pandas processed data into a torch built to be used with
        restricted Boltzmann machines
        '''
        MONTHS = 12
        WORDS = len(vocab_dict)

        torch_data = self.stored_dataset.copy()

        # All the ratings will be 0 at the beginning
        # First axis will be the [WORDS], then the [DAYS], and at the end the [MONTHS]
        data_temp = np.array([[ 0.0 ] * WORDS] * MONTHS)

        # the next output is somethingl like ['claro lfc apagar llama laguna yambo weba' '15' 1]
        # so I'll be accessing through the index
        for data in torch_data.values:
            for word in data[0].split(' '):

                if len(word) < 3:
                    continue

                word_idx = vocab_dict[word]
                month = data[2]

                data_temp[month][word_idx] += 1.0

        # what a hell I'm doing? Well, what I'm doing here is taking out all
        # the values that are not 0 ('cause 0 means there is no data) in order
        # to keep data semantic value. It's strange, I know, but life is hard
        # enough as to try yo improve this section of code, good luck person
        # of the future who are trying to understand it.
        non_zero_data = data_temp[data_temp != 0]

        mean =  non_zero_data.mean()
        std = non_zero_data.std()

        data_temp[data_temp != 0] = self.z_dsitribution(non_zero_data, mean, std)

        # how many times a word should repeat itself to be considered as an emergency word
        average_fr = mean * 1.5

        # -1 means the word is not present in any tweet
        data_temp[data_temp == 0] = -1

        # temporal data
        data_non_neg = data_temp[data_temp != -1]

        # 0 means data non related to emergency
        data_non_neg[data_non_neg < average_fr] = 0

        # 1 means it's probably related to an emergency event
        data_non_neg[data_non_neg != 0] = 1

        # putting temp data back to the main data set
        data_temp[data_temp != -1] = data_non_neg

        return data_temp

    def z_dsitribution(self, x, mean, std):
        return (x - mean) / std