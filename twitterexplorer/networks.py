## =============================================================================
## twitter explorer 
## network builders
## =============================================================================

import json
import igraph as ig
import pandas as pd
import numpy as np
import warnings
from itertools import combinations
from twitterexplorer.helpers import *

def get_edgelist(df,interaction_type):
    """Generate an edgelist from a Twitter CSV data collection.

    Parameters:
    df (pandas dataframe): dataframe containing the tweets in twitwi format
    interaction_type (str): retweet/quote/reply/mention
    
    Returns:
    interactions (pandas df): df reduced to the selected interactions
    tuples (pandas df): source/target/tweetid/timestamp pandas edgelist
    """    

    if interaction_type == 'retweet':
        interactions = df[df['retweeted_id'].notna()]
        tuples = interactions[['user_id','retweeted_user_id','id','timestamp_utc']]
        tuples = tuples.rename(columns={'user_id':'source',
                                        'retweeted_user_id':'target',
                                        'id':'tweetid',
                                        'timestamp_utc':'timestamp'})
    elif interaction_type == 'quote':
        interactions = df[(df['quoted_id'].notna())&(df['quoted_user_id'].notna())]
        tuples = interactions[['user_id','quoted_user_id','id','timestamp_utc']]
        tuples = tuples.rename(columns={'user_id':'source',
                                        'quoted_user_id':'target',
                                        'id':'tweetid',
                                        'timestamp_utc':'timestamp'})
    elif interaction_type == 'reply':
        interactions = df[df['to_userid'].notna()]
        tuples = interactions[['user_id','to_userid','id','timestamp_utc']]
        tuples = tuples.rename(columns={'user_id':'source',
                                        'to_user_id':'target',
                                        'id':'tweetid',
                                        'timestamp_utc':'timestamp'})
    elif interaction_type == 'mention':
        interactions = df[(df['mentioned_ids'].notna())&(df['mentioned_names'].notna())]
        interactions = interactions[(interactions['retweeted_id'].isna())&(interactions['quoted_id'].isna())&(interactions['to_userid'].isna())]
        interactions['mentioned_ids'] = interactions['mentioned_ids'].apply(string_to_list)
        interactions['mentioned_names'] = interactions['mentioned_names'].apply(string_to_list)        
        interactions = interactions.explode(['mentioned_ids','mentioned_names'])
        tuples = interactions[['user_id','mentioned_ids','id','timestamp_utc']]
        tuples = tuples.rename(columns={'user_id':'source',
                                        'mentioned_ids':'target',
                                         'id':'tweetid',
                                         'timestamp_utc':'timestamp'})        
        
    return interactions,tuples


# -----------------------------------------------------------------
# -----------------------------------------------------------------
# main part
# -----------------------------------------------------------------
# -----------------------------------------------------------------
def twitter_df_to_interactionnetwork(df,
                                     starttime,
                                     endtime,
                                     interaction_type
                                     ):
    """Generate Interaction Network from Twitter CSV data collection.

    Parameters:
    df (pandas dataframe): dataframe containing the tweets in twitwi format
    starttime (int): use retweets beginning on that date [timestamp]
    endtime (int): use retweets until on that date (including that last day) [timestamp]
    
    Returns:
    G (igraph graph object): retweet network where a link is created
    from i to j if i retweeted j
    """    
    
    idf = df.copy()
    
    # idf = idf[idf['user_id'].notna()]

    # reduce to the desired timerange
    if starttime != None and endtime != None:
        idf = idf[(idf['timestamp_utc'] >= starttime) & (idf['timestamp_utc']<= endtime)]    
    
    originaltweets = idf[(idf['retweeted_id'].isna())&(idf['quoted_id'].isna())]
    interactions,tuples = get_edgelist(idf,interaction_type)
    
    G = ig.Graph.TupleList(tuples.itertuples(index=False), 
                           directed=True, 
                           weights=False,
                           edge_attrs=['tweetid','timestamp']
                           ) 
                                  
    ## fill out the node metadata
    id2info = df[['user_id','user_screen_name','user_followers','user_friends']].groupby('user_id').agg('last').to_dict(orient='index')
    if interaction_type == 'retweet':
        id2info2 = df[['retweeted_user_id','retweeted_user']].rename(columns={'retweeted_user_id':'user_id','retweeted_user':'user_screen_name'}).groupby('user_id').agg('last').to_dict(orient='index')
    elif interaction_type == 'quote':
        id2info2 = df[['quoted_user_id','quoted_user']].rename(columns={'quoted_user_id':'user_id','quoted_user':'user_screen_name'}).groupby('user_id').agg('last').to_dict(orient='index')
    elif interaction_type == 'reply':
        id2info2 = df[['to_userid','to_username']].rename(columns={'to_userid':'user_id','to_username':'user_screen_name'}).groupby('user_id').agg('last').to_dict(orient='index')
    elif interaction_type == 'mention':
        id2info2 = interactions[['mentioned_ids','mentioned_names']].rename(columns={'mentioned_ids':'user_id','mentioned_names':'user_screen_name'}).groupby('user_id').agg('last').to_dict(orient='index')

    originaltweetids_dict = originaltweets[['user_id','id']].groupby('user_id')['id'].apply(list)
    interactiontweetids_dict = interactions[['user_id','id']].groupby('user_id')['id'].apply(list)        

    for v in G.vs:
        user_id_str = v['name']
        try:
            v['screen_name'] = id2info[user_id_str]['user_screen_name']
            v['followers'] = id2info[user_id_str]['user_followers']
            v['friends'] = id2info[user_id_str]['user_friends']
        except KeyError:
            try:
                v['screen_name'] = id2info2[user_id_str]['user_screen_name']
            except KeyError:
                v['screen_name'] = 0
            v['followers'] = 0
            v['friends'] = 0   
        try:
            v['originaltweets'] = originaltweetids_dict[user_id_str]
        except KeyError:
            v['originaltweets'] = "None"
        try:
            v['interactions'] = interactiontweetids_dict[user_id_str]
        except KeyError:
            v['interactions'] = "None"    
            
    return G

def reduce_network(G,
                   giant_component=False, 
                   aggregation=None,
                   hard_agg_threshold=0,
                   remove_self_loops=True):
    """Reduce network by aggregating nodes / links.

    Parameters:
    G (igraph graph object): retweet / mentions network
    giant_component (boolean): reduce network to largest connected component
    aggregation (str): 'soft' to remove nodes that are never retweeted and retweet only one user,
    'hard' to remove nodes that are retweeted less than {hard_agg_threshold} times.
    hard_agg_threshold(int)
    
    Returns:
    G (igraph graph object): reduced network
    """        
    t = hard_agg_threshold
    
    # giant_component == False and aggregation == None
    if giant_component == False and aggregation == None:
        pass

    # giant_component == True and aggregation == None
    elif giant_component == True and aggregation == None:
        G = G.components(mode="weak").giant()

    # giant_component == False and aggregation == 'hard'
    elif giant_component == False and aggregation == 'hard':
        todel = []
        for v in G.vs:
            if G.degree(v, mode="in") < t:
                todel.append(v.index)
        G.delete_vertices(todel)

    # giant_component == True and aggregation == 'hard'
    elif giant_component == True and aggregation == 'hard':
        todel = []
        for v in G.vs:
            if G.degree(v, mode="in") < t:
                todel.append(v.index)
        G.delete_vertices(todel)
        G = G.components(mode="weak").giant()

    # giant_component == False and aggregation == 'soft'
    elif giant_component == False and aggregation == 'soft':
        #G = G.components(mode="weak").giant()
        todel = []
        for v in G.vs:
            if G.degree(v, mode="in") == 0 and len(set(G.neighbors(v, mode="out"))) < 2:
                todel.append(v.index)
        G.delete_vertices(todel)

    # giant_component == True and aggregation == 'soft'
    elif giant_component == True and aggregation == 'soft':
        G = G.components(mode="weak").giant()
        todel = []  
        for v in G.vs:
            if G.degree(v, mode="in") == 0 and len(set(G.neighbors(v, mode="out"))) < 2:
                todel.append(v.index)
        G.delete_vertices(todel)

    # if remove_self_loops == True:
    #     G = G.simplify(multiple=False,loops=True)

    return G

def d3_rtn(G,private=False):
    """Generate d3js-compatible graph from igraph retweet network.

    Parameters:
    G (igraph graph): retweet network
    private (boolean): if private is true, nodes with less than 5000 followers are rendered unclickable
    
    Returns:
    d3js graph in json format {'nodes':[], 'links':[]}
    """    
    d3graph = {'nodes': [], 'links': []}
    for v in G.vs:
        ndict = {}
        node_id = v.index
        ndict["id"] = node_id
        ndict["twitter_id"] = v["name"]
        ndict["screen_name"] = v["screen_name"]
        ndict["followers"] = v["followers"]
        ndict["friends"] = v["friends"]
        ndict["interactions"] = v["interactions"]
        ndict["otweets"] = v["originaltweets"]        
        ndict["in_degree"] = G.degree(v, mode='in')
        ndict["out_degree"] = G.degree(v, mode='out')
        
        if private == True:
            if ndict['followers'] < 5000:
                ndict['twitter_id'] = "NaN"
                ndict['screen_name'] = "NaN"
                ndict['tweets'] = "NaN"
        
        try:
            ndict["louvain_com"] = v["louvain_com"]
        except KeyError:
            pass
        try:
            ndict["leiden_com"] = v["leiden_com"]
        except KeyError:
            pass
        try:
            ndict["infomap_com"] = v["infomap_com"]
        except KeyError:
            pass
        try:
            ndict["sbm_com"] = v["sbm_com"]
        except KeyError:
            pass                
        d3graph['nodes'].append(ndict)
    for link in G.es:
        ldict = {}
        source = link.source
        target = link.target
        tweetid = link['tweetid']
        timestamp = link['timestamp']
        ldict = {'source': source, 
                 'target': target,
                 'tweet': tweetid,
                 'ts':timestamp}
        d3graph['links'].append(ldict)
    return d3graph
    
def d3_cg_rtn(G):
    """Generate d3js-compatible graph from igraph cluster graph.

    Parameters:
    G -- cluster graph (igraph format)
    
    Returns:
    d3js graph in json format {'nodes':[], 'links':[]}
    """        
    d3graph = {'nodes': [], 'links': []}
    #print("Exporting...")
    for v in G.vs:
        ndict = {}
        name = v.index
        ndict["id"] = name
        ndict["name"] = f"Community {name + 1}"
        ndict["followers"] = int(v["followers"])
        ndict["friends"] = int(v["friends"])
        ndict["N"] = int(v["weight"])
        ndict["in_degree"] = G.degree(v, mode='in')
        ndict["out_degree"] = G.degree(v, mode='out')
        d3graph['nodes'].append(ndict)
    for link in G.es:
        ldict = {}
        source = link.source
        target = link.target
        weight = link['weight']
        ldict = {'source': source, 
                 'target': target,
                 'weight': weight}
        d3graph['links'].append(ldict)
    return d3graph

def convert_graph(G, savename):
    """Convert igraph graph to gml, csv and gv.

    Parameters:
    G (igraph graph): cluster graph
    savename (str): path to save the networks

    Returns:
    saves the networks to savename
    """        
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    G.write_gml(savename + '.gml')
    G.write_edgelist(savename + '.csv')
    G.write_dot(savename + '.gv')
    warnings.filterwarnings("default", category=RuntimeWarning)

def twitter_df_to_hashtagnetwork(df,
                                 starttime=None,
                                 endtime=None):
    hdf = df.copy()
    if starttime != None and endtime != None:
        hdf = hdf[(hdf['timestamp_utc'] >= starttime) & (hdf['timestamp_utc']<= endtime)]
    hdf = hdf[hdf['hashtags'].notna()]
    hdf = hdf[hdf['hashtags'].str.contains('|')]
    cohashtags = list(hdf['hashtags'])
    times = list(hdf['timestamp_utc'])
    edgelist = []
    for idx,cohashtag in enumerate(cohashtags):
        hashtaglist = cohashtag.split('|')
        combs = list(combinations(hashtaglist,2))
        for comb in combs:
            comb = list(comb)
            comb.append(times[idx])
            edgelist.append(comb)

    H = ig.Graph.DictList(edges=(dict(source=source, target=target, time=time, weight=1) for source, target, time in edgelist), 
                          vertices=None, 
                          directed=False)

    return H

def reduce_semanticnetwork(H,
                           giant_component=False,
                           node_threshold=0,
                           link_threshold=0,
                          ):
    
    # take the giant component
    if giant_component == True:
        H = H.components().giant()
    
    # remove nodes that have too low weight
    if node_threshold > 0:
        todel = []
        for v in H.vs:
            if H.degree(v) <= node_threshold:
                todel.append(v.index)
        H.delete_vertices(todel)        
        if giant_component == True:
            H = H.components().giant()
    
    H = H.simplify(multiple=True,combine_edges=dict(source="first", 
                                                    target="first",
                                                    time="first",
                                                    weight="sum"))

    # remove links that have too low weight
    if link_threshold > 0:
        todel = []
        for e in H.es:
            if e['weight'] <= link_threshold:
                todel.append(e)
        H.delete_edges(todel)
        if giant_component == True:
            H = H.components().giant()
    return H               

def d3_htn(G):
    """Generate d3js-compatible graph from igraph retweet network.

    Parameters:
    G (igraph graph) -- retweet network
    
    Returns:
    d3js graph in json format {'nodes':[], 'links':[]}
    """        
    d3graph = {'nodes': [], 'links': []}

    for v in G.vs:
        ndict = {}
        name = v['name']
        ndict["id"] = v.index
        ndict["name"] = name
        ndict["degree"] = G.degree(v)
        try:
            ndict["louvain_com"] = v["louvain_com"]
        except KeyError:
            pass    
        try:
            ndict["leiden_com"] = v["leiden_com"]
        except KeyError:
            pass        
        d3graph['nodes'].append(ndict)
    for link in G.es:
        ldict = {}
        source = link.source
        target = link.target
        weight = int(link['weight'])
        ldict = {'source': source, 
                 'target': target,
                 'weight': weight}
        d3graph['links'].append(ldict)
    
    return d3graph