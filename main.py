import tweepy
from extraction.datastream import StreamListener
from extraction.preproccesing import Preprocessing

stream_listener = StreamListener()

# The online box coordinates generation can be found
# here:
# https://boundingbox.klokantech.com/

Preprocessing.download()

stream_listener.filter(
    track=["emergencia", "covid", "pandemia", "robo"],
    languages=["es"],
    locations=[  # box constraint
        -83.3316391676, -5.1187465939, -75.9297537872, 2.366695812
    ]
)
