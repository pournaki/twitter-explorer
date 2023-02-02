## =============================================================================
## twitter explorer 
## converters
## =============================================================================

import csv
import json
import igraph as ig
from twitwi import normalize_tweet
from twitwi import format_tweet_as_csv_row
from twitwi.constants import TWEET_FIELDS
import warnings

def twitterjsonl_to_twitwicsv(input_filename):
    output_filename = input_filename.replace("jsonl","csv")
    with open (input_filename,"r",encoding="utf-8") as r:
        with open (output_filename,"w",encoding="utf-8") as o:
            w = csv.writer(o)
            w.writerow(TWEET_FIELDS)
            for line in r:
                tweet_json = json.loads(line)
                tweet_normalized = normalize_tweet(tweet_json,collection_source='twitterexplorer')
                tweet_csvrow = format_tweet_as_csv_row(tweet_normalized)
                w.writerow(tweet_csvrow)

def export_graph(G, savename):
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
