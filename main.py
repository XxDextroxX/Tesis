import tweepy
from extraction.datastream import StreamListener
# from extraction.preproccesing import Preprocessing

stream_listener = StreamListener()

# The online box coordinates generation can be found
# here:
# https://boundingbox.klokantech.com/

# Preprocessing.download()

# stream_listener.sample(
#     languages = ["es"],
#     # threaded = True
# )
stream_listener.filter(
    # track = list_1 + list_2 + list_3 + list_4 + list_5 + list_6 + list_7 + list_8,
    languages=["es"],
    # filter_level = "low",
    locations=[  # box constraint
        -83.3443261945,-4.6485920843,-76.1730794131,2.5029242769,
        # -93.452607978,-2.3069478112,-88.091279853,2.0425817528
    ],
)
