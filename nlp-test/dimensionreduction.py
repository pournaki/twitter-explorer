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
import umap.umap_ as umap
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

# load data from csv
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

#removing trailing whitespaces
corpus = list(map(lambda x: ' '.join([token for token in x.split()]), corpus))
#print("The text: \n", corpus)


import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# stopwords

stopwords_twitter = stopwords.words("german")
stopwords_twitter.append("rt")
stopwords_twitter.append(stopwords.words("english"))

tokenized = list(map(lambda x: word_tokenize(x), corpus))
tokenized = [[word for word in x if word not in stopwords_twitter] for x in tokenized]
#print("Stopwordized corpus: \n", tokenized)

# lemmatization
tagger_de = ht.HanoverTagger('morphmodel_ger.pgz')
tagger_en = ht.HanoverTagger('morphmodel_en.pgz')

lemmatized = [[tagger_en.analyze(word)[0].lower() for word in x] for x in tokenized]
#print("After Lemmatization: \n", lemmatized)

# finalized
final = list(zip(list(df_new2["text"].keys()), lemmatized))
#print(final)

from sklearn.feature_extraction.text import TfidfVectorizer
tfidf = TfidfVectorizer(tokenizer=lambda i:i, lowercase=False)
result = tfidf.fit_transform(lemmatized)

final2 = list(zip(list(df_new2["text"].keys()), result))
#print(final2)

# PCA

pca = PCA(n_components=2)
pca.fit(result.toarray())
pca2D = pca.transform(result.toarray())

# explained pca variance ratio
print(pca.explained_variance_ratio_)


# MDS

mds = MDS(n_components=2)
mds2D = mds.fit_transform(result.toarray())


# UMAP

umap_reducer = umap.UMAP()
umap2D = umap_reducer.fit_transform(result.toarray())



import matplotlib.pyplot as plt
plt.scatter(pca2D[:,0], pca2D[:,1], color="b")
plt.scatter(mds2D[:,0], mds2D[:,1], color="r")
plt.scatter(umap2D[:,0], umap2D[:,1], color="g")

plt.show()