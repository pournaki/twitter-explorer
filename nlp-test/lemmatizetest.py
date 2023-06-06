import sys
sys.path.append("/home/felix/Documents/bif/inno2/twitter-explorer/")

import os
import pandas as pd
import numpy as np
import altair as alt
import streamlit as st
import datetime as dt
import spacy
import time

from HanTa import HanoverTagger as ht
from sklearn.decomposition import PCA
from sklearn.manifold import MDS
from sklearn.metrics import silhouette_score

from twitterexplorer.legacy import *
from twitterexplorer.helpers import *
from twitterexplorer.streamlitutils import *
from twitterexplorer.plotting import *
from twitterexplorer.converters import twitterjsonl_to_twitwicsv
from twitterexplorer.converters import export_graph
from twitterexplorer.defaults import *
from twitterexplorer.constants import *
from twitterexplorer.__version__ import __version__
from twitterexplorer.networks import InteractionNetwork
from twitterexplorer.networks import SemanticNetwork




import nltk #Natural Language ToolKit is a library for NLP from Steven Bird, Ewan Klein, and Edward Loper (2009).
import re #to deal with regular expressions
import string #A collection of string constants       



def load_data_old(path):
        ## pandas does strange things to IDs, like importing them as ints and using
        ## scientific notation, so we need to make sure they are read as strings
        try:
            df = pd.read_csv(path,
                             dtype={"id":str,
                                    "user_id":str,
                                    "to_userid":str,
                                    "to_tweetid":str,
                                    "retweeted_id":str,
                                    "retweeted_user_id":str,
                                    "quoted_id":str,
                                    "quoted_user_id":str,
                                    "mentioned_ids":str,
                                    "mentioned_names":str,
                                    "hashtags":str
                                    },
                            low_memory=False,
                            # lineterminator='\n'
                         )
        except pd.errors.ParserError:
        ## https://stackoverflow.com/a/48187106
            df = pd.read_csv(path,
                             dtype={"id":str,
                                    "user_id":str,
                                    "to_userid":str,
                                    "to_tweetid":str,
                                    "retweeted_id":str,
                                    "retweeted_user_id":str,
                                    "quoted_id":str,
                                    "quoted_user_id":str,
                                    "mentioned_ids":str,
                                    "mentioned_names":str,
                                    "hashtags":str
                                    },
                            low_memory=False,
                            lineterminator='\n'
                         )            
        ## remove possible duplicates, even though the collector
        ## should not collect doubles
        df = df.drop_duplicates('id')
        df = df.drop_duplicates('id',keep='last')
        return df




start = time.time()
#example text from wikipedia
df = load_data_old("/home/felix/twitterexplorer/data/salzburg.csv")
df_new = df[['user_id', 'text']]
df_new2 = df_new.groupby(['user_id']).agg("\n".join)


corpus_original = df_new2['text'].values.tolist()



#print("The text original: \n", corpus_original)

#lower-casing the text
corpus = list(map(lambda x: x.lower(), corpus_original))


#print("The text lower case: \n", corpus)


corpus = list(map(lambda x: re.sub(r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&\/\/=]*)', '', x), corpus))
#print("The text without links: \n", corpus)

#removing digits from the text
corpus = list(map(lambda x: re.sub(r'\d+', '', x), corpus))
#print("The text without digits: \n", corpus)

#removing punctuation marks
corpus = list(map(lambda x: re.sub(r"[!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~]", '', x), corpus))

#removing everything else
corpus = list(map(lambda x: re.sub(r'[^\w\s]', '', x), corpus))

#print("The text without punctuation marks: \n", corpus)

#
#removing trailing whitespaces
corpus = list(map(lambda x: ' '.join([token for token in x.split()]), corpus))
#print("The text: \n", corpus)

#We are ready to start tokenizing the text using spaCy (and nltk)
#Run in UNIX shell: python3 -m spacy download en_core_web_sm



import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

#stopwords

stopwords_twitter = stopwords.words("german")
stopwords_twitter.append("rt")
stopwords_twitter.append(stopwords.words("english"))
#print("stopwords: \n", stopwords_twitter)
tokenized = list(map(lambda x: word_tokenize(x), corpus))

#print("Tokenized Corpus: \n", tokenized)
#remove stopwords
tokenized = [[word for word in x if word not in stopwords_twitter] for x in tokenized]
#tokenized = [word for word in tokenized if not word in stopwords_twitter]
#print("Stopwordized corpus: \n", tokenized)

#We are ready to execute stemming

# from nltk.stem import PorterStemmer

# stemmer = PorterStemmer()
# stemmed = [stemmer.stem(word) for word in tokenized]
# print("After Stemming: \n", stemmed)

#We are ready to execute lemmatization

tagger_de = ht.HanoverTagger('morphmodel_ger.pgz')
tagger_en = ht.HanoverTagger('morphmodel_en.pgz')



lemmatized = [[tagger_de.analyze(word)[0].lower() for word in x] for x in tokenized]
#print("After Lemmatization: \n", lemmatized)

final = list(zip(list(df_new2["text"].keys()), lemmatized))
#print(final)

from sklearn.feature_extraction.text import TfidfVectorizer

#tfidf = TfidfVectorizer(tokenizer=lambda i:i, lowercase=False)
#result = tfidf.fit_transform(lemmatized)


import gensim.downloader as api
from gensim.models import KeyedVectors

glove_model = api.load("glove-twitter-25")

def aggregate_vector(words):
    word_vectors = [glove_model[word] for word in words if word in glove_model]
    return np.mean(word_vectors, axis=0)

#print(lemmatized)

user_vectors = [aggregate_vector(user_tweets) for user_tweets in lemmatized]

#print(final)
#print(user_vectors)


final2 = list(zip(list(df_new2["text"].keys()), user_vectors))
#print(final2)

# print("halfway\n")
# pca = PCA(n_components=2)

# pca.fit(result.toarray())
# # #print(pca.explained_variance_ratio_)
# # print("pca")
# #klassisch mds lineare dimensionsreduktion, umap noch probieren
# # mds = MDS(n_components=2)
# # mds2D = mds.fit_transform(result.toarray())

# # print("mds")
# #print(mds2D)

# import umap
# from umap.umap_ import UMAP

# reducer = UMAP(n_components=2, metric="cosine")
# umap2d = reducer.fit_transform(result.toarray())


# import matplotlib.pyplot as plt
# data2Dpca = pca.transform(result.toarray())
# plt.scatter(data2Dpca[:,0], data2Dpca[:,1], color="b")
# #plt.scatter(mds2D[:,0], mds2D[:,1], color="r")
# plt.scatter(umap2d[:,0], umap2d[:,1], color="green")

# plt.show()

df = load_data("/home/felix/twitterexplorer/data/salzburg.csv")
G = InteractionNetwork()
G.build_network(pandas_dataframe=df,
                language_filter=None,
                interaction_type="retweet",
                starttime=None,
                endtime=None)
G.reduce_network(giant_component=True,
                    aggregation="soft",
                    hard_agg_threshold=0)

G_comdec = G._graph.copy()
G_comdec.vs['weight'] = 1
if 'weight' not in G_comdec.edge_attributes():
    G_comdec.es['weight'] = 1
G_comdec = G_comdec.simplify(multiple=True,
                                loops=True,
                                combine_edges={'tweetid':'ignore',
                                            'timestamp':'ignore',
                                            'weight':'sum'})    
G_comdec.to_undirected(mode='collapse',combine_edges={'weight':'sum'})
partition_leiden = G_comdec.community_leiden(objective_function='modularity') 

#print(partition_leiden.membership)

#print(type(final2[1]))

final3 = [list(t) for t in final2]
for x in final3:
    try:
        x.append(partition_leiden.membership[final3.index(x)])
    except:
        x.append(None)

# print(final3)

# features = np.array([item[1].toarray()[0] for item in final3]) 
# labels = np.array([item[2] for item in final3 if item[2] is not None])

final4 = [item for item in final3 if item[2] is not None]

#print(final4)


features = np.array([item[1] for item in final4]) 
labels = np.array([item[2] for item in final4 if item[2] is not None])

#print("this", features)
#print(labels)

score = silhouette_score(features, labels, metric="euclidean")
#cosine similarity verwenden


print(score)

#print(list(result[:])[0])
#for user in final2


end = time.time()
print("time: ", end-start)