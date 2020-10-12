#!/usr/bin/env python

"""Transforms Twitter data to networks.

Returns retweet networks (link from i to j if i retweets j)
and hashtag networks (link between i and j if i and j appear in
the same tweet) from Twitter data as igraph networks.

Returns community partition (Louvain, Infomap) as node attributes
and cluster graphs of the above networks.

Converts the igraph networks to d3js format for interactive
visualization.
"""

import json
import warnings
from datetime import datetime
import json_lines
from itertools import combinations
import igraph as ig
import louvain

__author__    = "Armin Pournaki"
__copyright__ = "Copyright 2020, Armin Pournaki"
__credits__   = ["Felix Gaisbauer", "Sven Banisch", "Eckehard Olbrich"]
__license__   = "GPLv3"
__version__   = "0.1"
__email__     = "pournaki@mis.mpg.de"

def json_to_jsonl(filename):
    """Transform nested json (legacy format) to jsonl.
    
    Parameters:
    filename (str): path to json to transform.

    Returns:
    saves the jsonl in the same dir as input json.
    """
    with open (filename, "r", encoding = 'utf-8') as f:
        tweetjson = json.load(f)
    jsonarray = tweetjson["tweets"]
    newfilename = filename + 'l'
    with open (newfilename, "w", encoding="utf-8") as f:
        for element in jsonarray:
            json.dump(element, f)
            f.write("\n")


def retweetnetwork(filename, 
                   giant_component=False, 
                   privacy=False,
                   aggregation=None,
                   t=0,
                   starttime=None,
                   endtime=None):
    """Generate Retweet Network from Twitter data collection.

    Parameters:
    filename: path to jsonl twitter object to transform
    giant_component (boolean): keep only largest weakly connected component 
    aggregation (str): aggregation method to use ('soft', 'hard', 'None')
    privacy: 
    t (int): threshold for hard aggregation
    
    Returns:
    igraph graph object: retweet network where a link is created
    from i to j if i retweeted j.
    """    
    with open(filename, 'rb') as f:    
        nodesdict = {}
        edgelist = []
        d3graph = {"nodes": [], "links": []}
        
        #print("Reading file...")

        for tweet in (json_lines.reader(f)):
            if 'retweeted_status' in tweet:
                
                time = tweet["created_at"]
                time = datetime.strptime(time,'%a %b %d %X %z %Y')
                time_date = time.date()

                if starttime <= time_date <= endtime:

                    # retweeting node [source of retweet action]                
                    name = tweet["user"]["screen_name"]
                    try:
                        nodesdict[f"{name}"]["followers"] = tweet["user"]["followers_count"]
                        nodesdict[f"{name}"]["friends"] = tweet["user"]["friends_count"]
                    except KeyError:
                        nodesdict[f"{name}"] = {}
                        nodesdict[f"{name}"]["followers"] = tweet["user"]["followers_count"]
                        nodesdict[f"{name}"]["friends"] = tweet["user"]["friends_count"]
                    try:
                        nodesdict[f"{name}"]["tweets"].append(tweet["id_str"])
                    except KeyError:
                        nodesdict[f"{name}"]["tweets"] = []
                        nodesdict[f"{name}"]["tweets"].append(tweet["id_str"])
                    
                    # retweeted node [target of retweet action]
                    name = tweet['retweeted_status']["user"]["screen_name"]
                    try:
                        nodesdict[f"{name}"]["followers"] = tweet['retweeted_status']["user"]["followers_count"]
                        nodesdict[f"{name}"]["friends"] = tweet['retweeted_status']["user"]["friends_count"]
                    except KeyError:
                        nodesdict[f"{name}"] = {}
                        nodesdict[f"{name}"]["followers"] = tweet['retweeted_status']["user"]["followers_count"]
                        nodesdict[f"{name}"]["friends"] = tweet['retweeted_status']["user"]["followers_count"]
                    try:
                        nodesdict[f"{name}"]["tweets"].append(tweet['retweeted_status']["id_str"])
                    except KeyError:
                        nodesdict[f"{name}"]["tweets"] = []
                        nodesdict[f"{name}"]["tweets"].append(tweet['retweeted_status']["id_str"])
                                    
                    # links
                    source   = tweet["user"]["screen_name"]                
                    target   = tweet['retweeted_status']['user']['screen_name']
                    tweetid  = tweet["id_str"]
                    time_str = time.isoformat(timespec='seconds')
                    edgelist.append((source, target, tweetid, time_str))
                
            
    #print("Importing to igraph...")
    # import to igraph
    G = ig.Graph.DictList(edges=(dict(source=source, target=target, tweet=tweetid,time=time, weight=1) for source, target, tweet, time in edgelist), 
                          vertices=None, 
                          directed=True)
   
    # add node metadata
    for v in G.vs:
        name = v['name']
        v['followers'] = nodesdict[name]['followers']
        v['friends'] = nodesdict[name]['friends']
        v['tweets'] = list(set(nodesdict[name]['tweets']))
    
    #print("Running giant component and aggregations...")
    
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
            if G.degree(v, mode="in") <= t:
                todel.append(v.index)
        #print("Deleting vertices")
        G.delete_vertices(todel)
        #G = G.components(mode="weak").giant()
    
    # giant_component == True and aggregation == 'hard'
    elif giant_component == True and aggregation == 'hard':
        todel = []
        for v in G.vs:
            if G.degree(v, mode="in") <= t:
                todel.append(v.index)
        #print("Deleting vertices")
        G.delete_vertices(todel)
        G = G.components(mode="weak").giant()
    
    # giant_component == False and aggregation == 'soft'
    elif giant_component == False and aggregation == 'soft':
        #G = G.components(mode="weak").giant()
        todel = []
        for v in G.vs:
            if G.degree(v, mode="in") == 0 and len(set(G.neighbors(v, mode="out"))) < 2:
                todel.append(v.index)
        #print("Deleting vertices")
        G.delete_vertices(todel)
        
            
    # giant_component == True and aggregation == 'soft'
    elif giant_component == True and aggregation == 'soft':
        G = G.components(mode="weak").giant()
        todel = []  
        for v in G.vs:
            if G.degree(v, mode="in") == 0 and len(set(G.neighbors(v, mode="out"))) < 2:
                todel.append(v.index)
        G.delete_vertices(todel)
    
    return G


def makeprivate(G):
    """Remove node metadata (name, tweets) from users with less than 5000 followers.

    Parameters:
    G: igraph graph object
    
    Returns:
    igraph graph object: retweet network with removed attributes for users
    with less than 5000 followers
    """    

    for e in G.es:
        source = e["source"]
        target = e["target"]
        source_n = G.vs.find(name=source)
        target_n = G.vs.find(name=target)
        if source_n["followers"] < 5000:
            e["source"] = str(source_n.index)
        if target_n["followers"] < 5000:
            e["target"] = str(target_n.index)
    for v in G.vs:
        if v["followers"] < 5000:
            v["name"] = str(v.index)
            v["tweets"] = ["None"]        
    return G

def d3_rtn(G):
    """Generate d3js-compatible graph from igraph retweet network.

    Parameters:
    G (igraph graph) -- retweet network
    
    Returns:
    d3js graph in json format {'nodes':[], 'links':[]}
    """    
    d3graph = {'nodes': [], 'links': []}
    #print("Exporting...")
    for v in G.vs:
        ndict = {}
        name = v['name']
        ndict["name"] = name
        ndict["followers"] = v["followers"]
        ndict["friends"] = v["friends"]
        ndict["tweets"] = v["tweets"]
        ndict["in_degree"] = G.degree(v, mode='in')
        ndict["out_degree"] = G.degree(v, mode='out')
        try:
            ndict["louvain_com"] = v["louvain_com"]
        except KeyError:
            pass
        try:
            ndict["infomap_com"] = v["infomap_com"]
        except KeyError:
            pass        
        d3graph['nodes'].append(ndict)
    for link in G.es:
        ldict = {}
        source = link['source']
        target = link['target']
        time   = link['time']
        tweetid = link['tweet']
        ldict = {'source': source, 
              'target': target,
              'time': time,
              'tweet': tweetid}
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
# --- HASHTAG NETWORKS ---

def hashtagnetwork(filename, 
                   giant_component=False,
                   remove_nodes=False,
                   threshold_remove=0,
                   starttime=None,
                   endtime=None):
    """Generate Hashtag Network from Twitter data collection.

    Parameters:
    filename: path to jsonl twitter object to transform
    giant_component (boolean): keep only largest weakly connected component 
    
    Returns:
    igraph graph object: hashtag network where a link is created
    between i to j if i and j appear in the same tweet.
    """        
    edgelist = []
    with open(filename, 'rb') as f:
        for tweet in json_lines.reader(f):

            time = tweet["created_at"]
            time = datetime.strptime(time,'%a %b %d %X %z %Y')
            time_date = time.date()

            if starttime <= time_date <= endtime:

                if len(tweet["entities"]["hashtags"]) > 1:
                    cohashtags = []
                    for element in tweet["entities"]["hashtags"]:
                        hashtag = element["text"]
                        cohashtags.append(hashtag)
                    combs = list(combinations(cohashtags,2))
                    for element in combs:
                        source = element[0]
                        target = element[1]
                        time_str = time.isoformat(timespec='seconds')
                        edgelist.append((source, target, time_str))

    H = ig.Graph.DictList(edges=(dict(source=source, target=target, time=time, weight=1) for source, target, time in edgelist), 
                          vertices=None, 
                          directed=False)

    if giant_component == True:
        H = H.components().giant()
    
    if remove_nodes == True:
        t = threshold_remove
        todel = []
        for v in H.vs:
            if H.degree(v) <= t:
                todel.append(v.index)
        H.delete_vertices(todel)        
        if giant_component == True:
            H = H.components().giant()

    H.es['weight'] = 1
    #H = H.simplify(combine_edges=dict(weight="sum"))
    
    return(H)
    
def d3_cg_htn(G):
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
        ndict["N"] = int(v["weight"])
        ndict["degree"] = G.degree(v)
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

def d3_htn(G):
    """Generate d3js-compatible graph from igraph retweet network.

    Parameters:
    G (igraph graph) -- retweet network
    
    Returns:
    d3js graph in json format {'nodes':[], 'links':[]}
    """        
    d3graph = {'nodes': [], 'links': []}
    #print("Exporting...")
    for v in G.vs:
        ndict = {}
        name = v['name']
        ndict["name"] = name
        ndict["degree"] = G.degree(v)
        try:
            ndict["louvain_com"] = v["louvain_com"]
        except KeyError:
            pass        
        d3graph['nodes'].append(ndict)
    for link in G.es:
        ldict = {}
        source = link["source"]
        target = link["target"]
        ldict = {'source': source, 
              'target': target}
        d3graph['links'].append(ldict)

    dl = d3graph["links"]
    nodl = list({(v['source'], v['target']):v for v in dl}.values())
    d3graph["links"] = nodl    

    return d3graph


# --- COMMUNITY DETECTION ---

def community_detection(G, methods=['louvain', 'infomap'], infomap_trials=100):
    """Compute communities of an igraph network and generate cluster graphs.

    Parameters:
    G (igraph graph): retweet network or hashtag network
    methods (list of str): preferred method of community detection
    infomap_trials (int, default=100): amount of trials for infomap method

    Returns:
    G (igraph graph) with node attribute '{method}_com'
    C (igraph graph): one cluster graph per method
    """        
    G.vs['weight'] = 1
    #print("Computing communities...")
    if 'louvain' in methods:            
        #print("Louvain...")
        Louvain = louvain.find_partition(G, louvain.ModularityVertexPartition)        
        cg_louv = Louvain.cluster_graph(combine_vertices=dict(weight="sum", 
                                                              followers="sum", 
                                                              friends="sum"),
                                        combine_edges=dict(weight=sum))        
    if 'infomap' in methods:
        #print("Infomap...")
        Infomap = G.community_infomap(trials=infomap_trials)
        cg_info = Infomap.cluster_graph(combine_vertices=dict(weight="sum", 
                                                              followers="sum", 
                                                              friends="sum"),
                                        combine_edges=dict(weight=sum))        
    del G.vs['weight']
    del G.es['weight']
    if 'louvain' and 'infomap' in methods:
        for v in G.vs:
            v["louvain_com"]  = Louvain.membership[v.index]
            v["infomap_com"]  = Infomap.membership[v.index] 
        return G, cg_louv, cg_info
    if 'louvain' in methods and 'infomap' not in methods:
        for v in G.vs:
            v["louvain_com"]  = Louvain.membership[v.index]
        return G, cg_louv
    if 'infomap' in methods and 'louvain' not in methods:
        for v in G.vs:
            v["infomap_com"]  = Infomap.membership[v.index] 
        return G, cg_info
