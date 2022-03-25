## =============================================================================
## twitter explorer 
## community detectors
## =============================================================================

def compute_leiden(G):
    """Compute Leiden communities of an igraph network and generate cluster graph.

    Parameters:
    G (igraph graph): retweet network or hashtag network
    
    Returns:
    G (igraph graph) with node attribute 'leiden_com'
    clustergraph (igraph graph): graph where every node is a community
    """     
    
    G_leiden = G.copy()
    G_leiden.vs['weight'] = 1
    if 'weight' not in G_leiden.edge_attributes():
        G_leiden.es['weight'] = 1
    G_leiden = G_leiden.simplify(multiple=True,
                                 loops=True,
                                 combine_edges={'tweetid':'ignore',
                                        'timestamp':'ignore',
                                        'weight':'sum'})    
    G_leiden.to_undirected(mode='collapse',combine_edges={'weight':'sum'})

    partition = G_leiden.community_leiden(objective_function='modularity')   
    clustergraph = partition.cluster_graph(combine_vertices=dict(weight="sum", 
                                                          followers="sum", 
                                                          friends="sum"),
                                          combine_edges=dict(weight=sum))

    for v in G.vs:
        v["leiden_com"]  = partition.membership[v.index]
    return G, clustergraph


def compute_louvain(G):
    """Compute Louvain communities of an igraph network and generate cluster graph.

    Parameters:
    G (igraph graph): retweet network or hashtag network
    
    Returns:
    G (igraph graph) with node attribute 'louvain_com'
    clustergraph (igraph graph): graph where every node is a community
    """     

    import louvain
    G_louvain = G.copy()
    G_louvain.vs['weight'] = 1
    if 'weight' not in G_louvain.edge_attributes():
        G_louvain.es['weight'] = 1
    partition = louvain.find_partition(G_louvain, louvain.ModularityVertexPartition)        
    clustergraph = partition.cluster_graph(combine_vertices=dict(weight="sum", 
                                                          followers="sum", 
                                                          friends="sum"),
                                         combine_edges=dict(weight=sum))
    for v in G.vs:
        v["louvain_com"]  = partition.membership[v.index]
    return G, clustergraph
