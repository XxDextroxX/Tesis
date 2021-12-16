from recommender_engine.engine import RBM
from recommender_engine.vocabulary import VocabularyHelper
from recommender_engine.dataset import DatasetHelper

print("Starting the training of RBM | initializing 0%")
vocabulary_helper = VocabularyHelper()
dataset_helper = DatasetHelper('data_streaming_preprocessing.csv')

### Vocabulary generetion
print("Starting the training of RBM | processing vocab 5%")
vocabulary_helper.build_vocab()
vocab, inv_vocab = vocabulary_helper.get_vocab()

print("Starting the training of RBM | building dataset 10%")
dataset_helper.build_dataset()
torch_data = dataset_helper.transform_torch(vocab)

nv = len(vocab) # visible nodes
nh = 100 # hidden nodes. Not related with any data field

print("Starting the training of RBM | training 30%")
rbm = RBM(nv, nh)
rbm.fit(100, torch_data)

print("Starting the training of RBM | done 100%")


