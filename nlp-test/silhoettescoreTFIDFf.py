import sys
sys.path.append("/home/dominik/Documents/twitter explorer/twitter-explorer")

import pandas as pd
import numpy as np
import time

from HanTa import HanoverTagger as ht
from sklearn.metrics import silhouette_score

from twitterexplorer.__version__ import __version__
from twitterexplorer.networks import InteractionNetwork

import re #to deal with regular expressions

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
df = load_data_old("/home/dominik/twitterexplorer/data/Salzburg.csv")

df_new = df[['user_id', 'text']]
df_new2 = df_new.groupby(['user_id']).agg("\n".join)

corpus_original = df_new2['text'].values.tolist()
#print("The text original: \n", corpus_original)

#lower-casing the text
corpus = list(map(lambda x: x.lower(), corpus_original))

#removing urls
corpus = list(map(lambda x: re.sub(r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&\/\/=]*)', '', x), corpus))

#removing digits from the text
corpus = list(map(lambda x: re.sub(r'\d+', '', x), corpus))

#removing punctuation marks
corpus = list(map(lambda x: re.sub(r"[!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~]", '', x), corpus))

#removing everything else
corpus = list(map(lambda x: re.sub(r'[^\w\s]', '', x), corpus))

#removing trailing whitespaces
corpus = list(map(lambda x: ' '.join([token for token in x.split()]), corpus))

#print("The text: \n", corpus)



from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# stopwords
stopwords_twitter = stopwords.words("german")
stopwords_twitter.append("rt")
stopwords_twitter.append(stopwords.words("english"))

tokenized = list(map(lambda x: word_tokenize(x), corpus))
tokenized = [[word for word in x if word not in stopwords_twitter] for x in tokenized]

# lemmatization
tagger_de = ht.HanoverTagger('morphmodel_ger.pgz')
tagger_en = ht.HanoverTagger('morphmodel_en.pgz')

lemmatized = [[tagger_en.analyze(word)[0].lower() for word in x] for x in tokenized]

# finalized
final = list(zip(list(df_new2["text"].keys()), lemmatized))

from sklearn.feature_extraction.text import TfidfVectorizer

tfidf = TfidfVectorizer(tokenizer=lambda i:i, lowercase=False)
result = tfidf.fit_transform(lemmatized)

final2 = list(zip(list(df_new2["text"].keys()), result))
#print(final2)


# Compare leiden communities to calculated tfidf data

# building twitterexplorer interaction network to calculate leiden communities
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

# leiden communities
partition_leiden = G_comdec.community_leiden(objective_function='modularity') 
#print(partition_leiden.membership) 


# build features from tfidf data and labels from leiden communities
leidenlist = [list(t) for t in final2]
for x in leidenlist:
    try:
        x.append(partition_leiden.membership[leidenlist.index(x)])
    except:
        x.append(None)

leidenlist = [item for item in leidenlist if item[2] is not None]


features = np.array([item[1].toarray()[0] for item in leidenlist]) 
labels = np.array([item[2] for item in leidenlist if item[2] is not None])


# calculate mean silhouette scores for data
score = silhouette_score(features, labels, metric="euclidean")
#score = silhouette_score(features, labels, metric="cosine")

print(score)

end = time.time()
print("time: ", end-start)