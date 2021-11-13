import pandas as pd # managing CSV files

from twisted.internet import task, reactor # an event loop library
from extraction.datastream import StreamListener  # handle twitter's connection
#----------------------------------------------------------------------------------------


# NOTE: uncomment this if this is the first time you're gonna run it
# from extraction.preproccesing import Preprocessing
# Preprocessing.download()
#----------------------------------------------------------------------------------------

# loading list of keywords
NUMBER_LISTS = 14 # number of csv files with words
full_words = [] # this will contain all the words

assert NUMBER_LISTS > 0 # you need at least one of these files

# Loading all the words into an unique variable
for i in range(NUMBER_LISTS):
    full_words += [str(x[0]) for x in (pd.read_csv(f'./Listas/Lista{i + 1}.csv')).values]
#----------------------------------------------------------------------------------------


PERIOD = 240.0 # how often should the sample of words change

def event():
    # This will handle all the errors coming from Tweeter such as
    # extraction limit reached or disconnections
    stream_listener = StreamListener(full_words) # If you do this, Python will free up memory
    stream_listener.extract_tweets(sample_size=300)

event_loop = task.LoopingCall(event)
event_loop.start(PERIOD) # call every [period] seconds

# All the extraction will run inside the event loop
reactor.run()