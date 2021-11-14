import pandas as pd  # managing CSV files

from datetime import date
from dotenv import load_dotenv
from twisted.internet import task, reactor  # an event loop library
from extraction.datastream import StreamListener  # handle twitter's connection
import os
# ----------------------------------------------------------------------------------------


# NOTE: uncomment this if this is the first time you're gonna run it
# from extraction.preproccesing import Preprocessing
# Preprocessing.download()
# ----------------------------------------------------------------------------------------

# loading list of keywords
load_dotenv()
NUMBER_LISTS = int(os.getenv("NUMBER_LISTS"))  # number of csv files with words
full_words = []  # this will contain all the words

assert NUMBER_LISTS > 0  # you need at least one of these files

# Loading all the words into an unique variable
for i in range(NUMBER_LISTS):
    full_words += [str(x[0])
                   for x in (pd.read_csv(f'./Listas/Lista{i + 1}.csv')).values]
# ----------------------------------------------------------------------------------------


# how often should the sample of words change
PERIOD = int(os.getenv("REFRESH_TIME"))
SAMPLE_SIZE = int(os.getenv("WORD_SAMPLE_SIZE"))

def event():

    raw_path = f'./tweets_streaming_{str(date.today())}.json'

    # This will handle all the errors coming from Tweeter such as
    # extraction limit reached or disconnections
    # If you do this, Python will free up memory
    stream_listener = StreamListener(full_words, raw_data_path=raw_path)
    stream_listener.extract_tweets(sample_size=SAMPLE_SIZE)


event_loop = task.LoopingCall(event)
event_loop.start(PERIOD)  # call every [period] seconds

# All the extraction will run inside the event loop
reactor.run()
