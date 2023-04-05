import sys
sys.path.append("/home/felix/Documents/bif/inno2/twitter-explorer/")

import os
import pandas as pd
import numpy as np
import altair as alt
import streamlit as st
import datetime as dt

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

#example text from wikipedia
df = load_data_old("/home/felix/twitterexplorer/data/wurst.csv")
print(df)
df_new = df[['user_screen_name', 'text']]
df_new2 = df_new.groupby(['user_screen_name']).agg("\n".join)
corpus_original = df_new2['text'].values.tolist()

print("The text: \n", corpus_original)

#lower-casing the text
corpus = list(map(lambda x: x.lower(), corpus_original))
print("The text: \n", corpus)


corpus = list(map(lambda x: re.sub(r'^https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$', '', x), corpus))
print("The text: \n", corpus)

#removing digits from the text
corpus = list(map(lambda x: re.sub(r'\d+', '', x), corpus))
print("The text: \n", corpus)

#removing punctuation marks
for x in corpus:
    x = x.translate(str.maketrans('', '', string.punctuation))
print("The text: \n", corpus)

#removing trailing whitespaces
#corpus = ' '.join([token for token in corpus.split()])
#print("The text: \n", corpus)

#We are ready to start tokenizing the text using spaCy (and nltk)
#Run in UNIX shell: python3 -m spacy download en_core_web_sm

import nltk
from nltk.tokenize import word_tokenize







#stpowirds




tokenized = word_tokenize(corpus)
#print("Tokenized Corpus: \n", tokenized)
#remove stopwords
tokenized = [word for word in tokenized if not word in stopwords_spacy]
#print("Tokenized corpus: \n", tokenized)

#We are ready to execute stemming
# from nltk.stem import PorterStemmer

# stemmer = PorterStemmer()
# stemmed = [stemmer.stem(word) for word in tokenized]
# print("After Stemming: \n", stemmed)

#We are ready to execute lemmatization
from nltk.stem import WordNetLemmatizer
nltk.download('wordnet')
nltk.download("omw-1.4")
lemmatizer=WordNetLemmatizer()

lemmatized = [lemmatizer.lemmatize(word) for word in tokenized]
#print("After Lemmatization: \n", lemmatized)

#We are ready to execute Part-of-Speech tagging
# doc = spacy_model(corpus_original)
# pos_tagged = [(token, token.pos_) for token in doc]
# print("POS-tagging: \n", pos_tagged)


def nlp_tweets(df):


    df_new = df[['user_screen_name', 'text']]
    df_new2 = df_new.groupby(['user_screen_name']).agg("\n".join)
    data = df_new2['text'].values.tolist()

    bow = CountVectorizer(min_df=2, max_features=10000)
    bow.fit(data)
    bow_df = bow.transform(data).toarray()
    df3 = pd.DataFrame(data = bow_df, columns = bow.get_feature_names_out())

    tfidf = TfidfVectorizer(min_df=2, max_features=10000)
    tfidf.fit(data)
    tfidf_df = tfidf.transform(data).toarray()

    pca = PCA(n_components=2)
    pca.fit(tfidf_df)

    data2D = pca.transform(tfidf_df)    
    df_new2['pcax'] = data2D[:,0]
    df_new2['pcay'] = data2D[:,1]
    df = df.merge(df_new2,how='left', left_on='user_screen_name', right_on='user_screen_name')
    return df


