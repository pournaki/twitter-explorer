## =============================================================================
## twitter explorer 
## network builders
## =============================================================================

import json
import igraph as ig
import pandas as pd
import numpy as np
from itertools import combinations
import louvain as louvain_method

from twitterexplorer.helpers import *
from twitterexplorer.d3networks import *
from twitterexplorer import __version__

# -----------------------------------------------------------------
# -----------------------------------------------------------------
# INTERACTION NETWORKS
# -----------------------------------------------------------------
# -----------------------------------------------------------------

class InteractionNetwork():

    def __init__(self):
        self._interaction_type = None
        self._graph = None        
        self._reduction_methods = {'giant_component':False,
                                  'aggregation':None,
                                  'aggregation_threshold':None}
        self._community_detection = {'louvain':False,
                                    'leiden':False}
        self._private = False       
        self._d3dict = None

    def build_network(self, 
                      pandas_dataframe,
                      interaction_type,
                      starttime=None,
                      endtime=None,
                      language_filter=None):
        """Generate Interaction Network from Twitter CSV data collection.

        Parameters:
        pandas dataframe: dataframe containing the tweets in twitwi format
        starttime (int): use retweets beginning on that date [timestamp]
        endtime (int): use retweets until on that date (including that last day) [timestamp]
        language_filter (list): list of ISO-code languages to keep

        Returns:
        self._graph (igraph graph object): retweet network where a link is created
        from i to j if i retweeted j
        """    

        idf = pandas_dataframe.copy()
        if language_filter != None:
            idf = idf[idf['lang'].isin(language_filter)]

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
        id2info = pandas_dataframe[['user_id','user_screen_name','user_followers','user_friends']].groupby('user_id').agg('last').to_dict(orient='index')
        if interaction_type == 'retweet':
            id2info2 = pandas_dataframe[['retweeted_user_id','retweeted_user']].rename(columns={'retweeted_user_id':'user_id','retweeted_user':'user_screen_name'}).groupby('user_id').agg('last').to_dict(orient='index')
        elif interaction_type == 'quote':
            id2info2 = pandas_dataframe[['quoted_user_id','quoted_user']].rename(columns={'quoted_user_id':'user_id','quoted_user':'user_screen_name'}).groupby('user_id').agg('last').to_dict(orient='index')
        elif interaction_type == 'reply':
            id2info2 = pandas_dataframe[['to_userid','to_username']].rename(columns={'to_userid':'user_id','to_username':'user_screen_name'}).groupby('user_id').agg('last').to_dict(orient='index')
        elif interaction_type == 'mention':
            id2info2 = pandas_dataframe[['mentioned_ids','mentioned_names']].rename(columns={'mentioned_ids':'user_id','mentioned_names':'user_screen_name'}).groupby('user_id').agg('last').to_dict(orient='index')

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
                
        self._graph = G
        self._interaction_type = interaction_type

    def reduce_network(self,
                       giant_component=False, 
                       aggregation=None,
                       hard_agg_threshold=0,
                       remove_self_loops=True):
        """Reduce network by aggregating nodes / links.

        Parameters:
        giant_component (boolean): reduce network to largest connected component
        aggregation (str): 'soft' to remove nodes that are never retweeted and retweet only one user,
        'hard' to remove nodes that are retweeted less than {hard_agg_threshold} times.
        hard_agg_threshold(int)
        
        Returns:
        G (igraph graph object): reduced network
        """    
        G = self._graph    
        t = hard_agg_threshold
        
        G.vs['in-degree-preagg'] = G.degree(mode="in")
        G.vs['out-degree-preagg'] = G.degree(mode="out")

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

        G.vs['in-degree'] = G.degree(mode="in")
        G.vs['out-degree'] = G.degree(mode="out")

        self._graph = G
        self._reduction_methods["giant_component"] = giant_component
        self._reduction_methods["aggregation"] = aggregation
        self._reduction_methods["aggregation_threshold"] = hard_agg_threshold

    def community_detection(self,louvain=True,leiden=False):
        """Compute Leiden communities of an igraph network and generate cluster graph.

        Parameters:
        louvain (boolean): compute Louvain communities
        leiden (boolean): compute Leiden communities
        
        Returns:
        self._graph (igraph graph) with additional node attributes for 
        """     
        G = self._graph

        ## prepare the graph for undirected community detection
        G_comdec = G.copy()
        G_comdec.vs['weight'] = 1
        if 'weight' not in G_comdec.edge_attributes():
            G_comdec.es['weight'] = 1
        G_comdec = G_comdec.simplify(multiple=True,
                                     loops=True,
                                     combine_edges={'tweetid':'ignore',
                                                    'timestamp':'ignore',
                                                    'weight':'sum'})    
        G_comdec.to_undirected(mode='collapse',combine_edges={'weight':'sum'})

        ## we may add the possibility to run the algorithm 
        ## several times 
        if leiden == True:
            partition_leiden = G_comdec.community_leiden(objective_function='modularity') 
            for v in G.vs:
                v["leiden_com"]  = partition_leiden.membership[v.index]
            self._community_detection['leiden'] = True
        if louvain == True:
            partition_louvain = louvain_method.find_partition(G_comdec, louvain_method.ModularityVertexPartition)
            for v in G.vs:
                v["louvain_com"]  = partition_louvain.membership[v.index]
            self._community_detection['louvain'] = True

        self._graph = G

    def build_d3dict(self,
                     search_query="",
                     collected_on="",
                     private=False):
        """Generate d3js-compatible graph dict from igraph interaction network.

        Parameters:
        search_query (str): search query used to collect the data (will be written in the final HTML)
        collected_on (str): date of the data collection (will be written in the final HTML)
        private (boolean): if private is true, nodes with less than 5000 followers are rendered unclickable
        
        Returns:
        self._d3dict (graph in json format {'nodes':[], 'links':[]})
        """    
        G = self._graph
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
            try:
                ndict["in_degree_pa"] = v['in-degree-preagg']
                ndict["out_degree_pa"] = v['out-degree-preagg']            
            except KeyError:
                pass
            
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
        
        timestamps = self._graph.es['timestamp']
        firstdate_str = str(dt.datetime.fromtimestamp(timestamps[-1]))[:16]
        lastdate_str = str(dt.datetime.fromtimestamp(timestamps[0]))[:16]        

        ## add the graph information
        d3graph['graph'] = {}
        d3graph['graph']['type'] = f"{self._interaction_type.capitalize()} network"
        d3graph['graph']['N_nodes'] = len(d3graph["nodes"])
        d3graph['graph']['N_links'] = len(d3graph["links"])
        d3graph['graph']['keyword'] = search_query
        d3graph['graph']['collected_on'] = collected_on
        d3graph['graph']['first_tweet'] = firstdate_str
        d3graph['graph']['last_tweet'] = lastdate_str
        d3graph['version_number'] = __version__

        self._d3dict = d3graph
        self._private = private    

    def write_html(self,output_path):
        """Export the d3dict as explorable HTML

        Parameters:
        output_path (str): where to save the HTML
        """
        if self._private == True:
            htmlstring = rtn_html_p(data=self._d3dict)
        elif self._private == False:
            htmlstring = rtn_html(data=self._d3dict)
        with open(output_path, "w",encoding='utf-8') as f:
            f.write(htmlstring)


# -----------------------------------------------------------------
# -----------------------------------------------------------------
# SEMANTIC NETWORKS
# -----------------------------------------------------------------
# -----------------------------------------------------------------

class SemanticNetwork():

    def __init__(self):
        self._graph = None        
        self._removed_hashtags = []
        self._reduction_methods = {'giant_component':False,
                                   'node_threshold':0,
                                   'link_threshold':0}                                
        self._community_detection = {'louvain':False,
                                     'leiden':False}
        self._d3dict = None
        

    def build_network(self, 
                      pandas_dataframe,
                      hashtags_to_remove=None,
                      starttime=None,
                      endtime=None,
                      language_filter=None):
        """Generate Semantic Network from Twitter CSV data collection.

        Parameters:
        pandas_dataframe: dataframe containing the tweets in twitwi format
        starttime (int): use retweets beginning on that date [timestamp]
        endtime (int): use retweets until on that date (including that last day) [timestamp]
        language_filter (list): list of ISO-code languages to keep

        Returns:
        self._graph (igraph graph object): retweet network where a link is created
        from i to j if i retweeted j
        """    

        hdf = pandas_dataframe.copy()
        if language_filter != None:
            hdf = hdf[hdf['lang'].isin(language_filter)]

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

        ## remove certain hashtags from the network
        if hashtags_to_remove != None:
            nodes_to_remove = []
            for ht in hashtags_to_remove:                        
                ht = ht.replace("#","")
                idx_of_ht = np.where(np.array(H.vs['name']) == ht)[0][0]
                nodes_to_remove.append(idx_of_ht)
            H.delete_vertices(nodes_to_remove)
        
        self._graph = H
        self._removed_hashtags = hashtags_to_remove

    def reduce_network(self,
                       giant_component=False,
                       node_threshold=0,
                       link_threshold=0,
                      ):
        """Reduce network by aggregating nodes / links.

        Parameters:
        giant_component (boolean): reduce network to largest connected component
        aggregation (str): 'soft' to remove nodes that are never retweeted and retweet only one user,
        'hard' to remove nodes that are retweeted less than {hard_agg_threshold} times.
        hard_agg_threshold(int)
        
        Returns:
        G (igraph graph object): reduced network
        """            
        H = self._graph

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

        self._graph = H   
        self._reduction_methods['giant_component'] = giant_component
        self._reduction_methods['node_threshold'] = node_threshold
        self._reduction_methods['link_threshold'] = link_threshold

    def community_detection(self,louvain=True,leiden=False):
        """Compute Leiden communities of an igraph network and generate cluster graph.

        Parameters:
        G (igraph graph): retweet network or hashtag network
        
        Returns:
        G (igraph graph) with additional node attribute 'leiden_com'
        """     
        G = self._graph

        ## we may add the possibility to run the algorithm 
        ## several times 
        if leiden == True:
            partition_leiden = G.community_leiden(objective_function='modularity') 
            for v in G.vs:
                v["leiden_com"]  = partition_leiden.membership[v.index]
            self._community_detection['leiden'] = True
        if louvain == True:
            partition_louvain = louvain_method.find_partition(G, louvain_method.ModularityVertexPartition)
            for v in G.vs:
                v["louvain_com"]  = partition_louvain.membership[v.index]
            self._community_detection['louvain'] = True

        self._graph = G


    def build_d3dict(self,
                     search_query="",
                     collected_on=""):
        """Generate d3js-compatible graph from igraph retweet network.

        Parameters:
        G (igraph graph) -- retweet network
        
        Returns:
        d3js graph in json format {'nodes':[], 'links':[]}
        """    
        G = self._graph    
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
        
        timestamps = self._graph.es['time']
        firstdate_str = str(dt.datetime.fromtimestamp(timestamps[-1]))[:16]
        lastdate_str = str(dt.datetime.fromtimestamp(timestamps[0]))[:16]        

        d3graph['graph'] = {}
        d3graph['graph']['type'] = "Hashtag network"
        d3graph['graph']['N_nodes'] = len(d3graph["nodes"])
        d3graph['graph']['N_links'] = len(d3graph["links"])
        d3graph['graph']['keyword'] = search_query
        d3graph['graph']['collected_on'] = collected_on
        d3graph['graph']['first_tweet'] = firstdate_str
        d3graph['graph']['last_tweet'] = lastdate_str
        d3graph['version_number'] = __version__

        self._d3dict = d3graph

    def write_html(self,output_path):
        htmlstring = htn_html(data=self._d3dict)
        with open(output_path, "w",encoding='utf-8') as f:
            f.write(htmlstring)
        