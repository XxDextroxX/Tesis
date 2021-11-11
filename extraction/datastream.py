from math import nan
import tweepy
import os
import json
import csv
from os.path import exists
from extraction.preproccesing import Preprocessing


class StreamListener(tweepy.Stream):

    def __init__(self):
        self.preprocessor = Preprocessing()
        self.lista_name_fields = ['user_id_str', 'status_id', 'created_at', 'screen_name',
                                  'text', 'status_url', 'lat', 'long', 'place_full_name', 'revisado']
        self.path_csv = './data_streaming.csv'
        self.should_create_file_csv = False
        self.path_tsv = './data_streaming_preprocessing.csv'
        self.should_create_file_tsv = False  # if the json file should be created or not
        self.path = "./tweets_streaming.json"
        self.should_create_file = False  # if the json file should be created or not
        self.consumer_key = "HRnrbF20nFjNBabu6W0d62dTa"  # twitter app key
        # twitter app secret
        self.consumer_secret = "1ZXn0mQbmw3AepGhMxTfSgybzB7KblHDWNjzEPe5iBZn1LVTf3"
        self.access_token = "908144452723773440-MBkl0CRLu37lsz8ygCTkzp4dwZ6gxuY"  # twitter key
        self.access_token_secret = "rZMpZ2QXCsfeoUfgKj7mtsZRJO1Bp1mLTjwuDVZafY9VY"  # twitter secret

        super().__init__(
            self.consumer_key, self.consumer_secret,
            self.access_token, self.access_token_secret
        )

    def on_status(self, status):
        if not hasattr(status, "retweeted_status"):
            try:
                self.save_raw_data(status._json)
                self.save_csv(status, self.path_csv)
                self.save_csv(status, self.path_tsv, True)
            except Exception as e:
                print(e)

    # the [file] should be a reference
    def save_raw_data(self, json_data):
        # If the file doesn't exist then I should write the
        # json structure.
        if not exists(self.path):
            self.should_create_file = True

        with open(self.path, "a+", encoding="utf-8") as f:

            # [f] is a reference
            self.delete_last_line(f)

            # What you wanna write
            content = ('[\n' if self.should_create_file else ',') + \
                f"{json.dumps(json_data)}\n]"

            if self.should_create_file:
                self.should_create_file = False

            f.write(content)  # replacing the last line
            f.flush()  # ensure file will be full writed before being readed again
            f.close()  # closing the file

    def save_csv(self, status, path, shouldPreprocessing=False):

        json_data = status._json
        lat = None
        long = None
        if not exists(path):
            self.should_create_file_csv = True
        with open(path, "a+", encoding='utf-8') as f:
            if self.should_create_file_csv:
                f.write("|".join(self.lista_name_fields))
                f.flush()
                self.should_create_file_csv = False
            if hasattr(status.coordinates, 'coordinates'):

                lat = status.coordinates.coordinates[0]
                long = status.coordinates.coordinates[1]
            else:
                if hasattr(status.place, 'bounding_box'):
                    lat = (
                        status.place.bounding_box.coordinates[0][1][0]+status.place.bounding_box.coordinates[0][3][0]) / 2
                    long = (
                        status.place.bounding_box.coordinates[0][1][1]+status.place.bounding_box.coordinates[0][3][1]) / 2
                else:
                    lat = 'na'
                    long = 'na'

            text = json_data['extended_tweet']['full_text']if hasattr(
                status, 'extended_tweet') else json_data['text']
            if shouldPreprocessing:
                text = self.preprocessor.clean_data(text)

            fields = [
                json_data['user']['id_str'],
                json_data['id_str'],
                json_data['created_at'],
                json_data['user']['screen_name'],
                text,
                json_data['entities']['media']['url'] if hasattr(
                    status.entities, 'media') else 'na',
                str(lat),
                str(long),
                json_data['place']['full_name'] if hasattr(
                    status.place, 'full_name') else 'na',
                'no'
            ]

            data = json.dumps('|'.join(fields))
            data = data[1:]
            data = data[:-1]
            f.write(data+'\n')

            f.flush()
            f.close()

    def delete_last_line(self, file):
        # Move the pointer (similar to a cursor in a text editor) to the end of the file
        file.seek(0, os.SEEK_END)

        # This code means the following code skips the very last character in the file -
        # i.e. in the case the last line is null we delete the last line
        # and the penultimate one
        pos = file.tell() - 1

        # Read each character in the file one at a time from the penultimate
        # character going backwards, searching for a newline character
        # If we find a new line, exit the search
        while pos > 0 and file.read(1) != "\n":
            pos -= 1
            file.seek(pos, os.SEEK_SET)

        # So long as we're not at the start of the file, delete all the characters ahead
        # of this position
        if pos > 0:
            file.seek(pos, os.SEEK_SET)
            file.truncate()

    def on_error(self, status_code):
        # status code 420 means Tweetir has blocked the API key due to api call limit
        # and if that happens then connection should be sutted off
        if status_code == 420:
            return False
