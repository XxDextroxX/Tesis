import tweepy
import pandas as pd
from extraction.datastream import StreamListener
# from extraction.preproccesing import Preprocessing

stream_listener = StreamListener()

# The online box coordinates generation can be found
# here:
# https://boundingbox.klokantech.com/

# Preprocessing.download()

# stream_listener.sample(
#     languages=["es"],
#     # threaded = True
# )
list_1 = [str(x[0]) for x in (pd.read_csv('./Listas/Lista1.csv')).values]
list_2 = [str(x[0]) for x in (pd.read_csv('./Listas/Lista2.csv')).values]
list_3 = [str(x[0]) for x in (pd.read_csv('./Listas/Lista3.csv')).values]
list_4 = [str(x[0]) for x in (pd.read_csv('./Listas/Lista4.csv')).values]
list_5 = [str(x[0]) for x in (pd.read_csv('./Listas/Lista5.csv')).values]
list_6 = [str(x[0]) for x in (pd.read_csv('./Listas/Lista6.csv')).values]
list_7 = [str(x[0]) for x in (pd.read_csv('./Listas/Lista7.csv')).values]
list_8 = [str(x[0]) for x in (pd.read_csv('./Listas/Lista8.csv')).values]
list_9 = [str(x[0]) for x in (pd.read_csv('./Listas/Lista9.csv')).values]
list_10 = [str(x[0]) for x in (pd.read_csv('./Listas/Lista10.csv')).values]
list_11 = [str(x[0]) for x in (pd.read_csv('./Listas/Lista11.csv')).values]
list_12 = [str(x[0]) for x in (pd.read_csv('./Listas/Lista12.csv')).values]
list_13 = [str(x[0]) for x in (pd.read_csv('./Listas/Lista13.csv')).values]
list_14 = [str(x[0]) for x in (pd.read_csv('./Listas/Lista14.csv')).values]


stream_listener.filter(
    # track = list_1 + list_2 + list_3 + list_4 + list_5 + list_6 + list_7 + list_8
    languages=["es"],
    track=list_1 + list_2 + list_3 + list_4 + list_5 + list_6 + \
    list_7 + list_8 + list_9+list_10+list_11+list_12+list_13+list_14,
    filter_level="low",
    locations=[  # box constraint
        -83.3443261945, -4.6485920843, -76.1730794131, 2.5029242769,
        # -93.452607978,-2.3069478112,-88.091279853,2.0425817528
    ],
)
