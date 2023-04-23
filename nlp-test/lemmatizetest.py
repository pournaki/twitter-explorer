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

start = time.time()
#example text from wikipedia
df = load_data("/home/felix/twitterexplorer/data/wurst.csv")
df_new = df[['user_screen_name', 'text']]
df_new2 = df_new.groupby(['user_screen_name']).agg("\n".join)

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

tfidf = TfidfVectorizer(tokenizer=lambda i:i, lowercase=False)

result = tfidf.fit_transform(lemmatized)

pca = PCA(n_components=2)

pca.fit(result.toarray())

mds = MDS(n_components=2)

mds2D = mds.fit_transform(result.toarray())

print(mds2D)



import matplotlib.pyplot as plt
data2Dpca = pca.transform(result.toarray())
plt.scatter(data2Dpca[:,0], data2Dpca[:,1], color="b")
plt.scatter(mds2D[:,0], mds2D[:,1], color="r")
end = time.time()
print("time: ", end-start)
plt.show()