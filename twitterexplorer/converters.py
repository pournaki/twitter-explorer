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
from ebbe import getpath

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

def normalize_zs_dict(zs_tweet_dict):
    if '__typename' in zs_tweet_dict['data'].keys():
        tweet = recombobulate_tweet(tweet_root=zs_tweet_dict['data'])
        tweet_normalized = normalize_tweet(tweet,extract_referenced_tweets=True)
        return tweet_normalized
    else:
        return []
        
def zeeschuimerjsonl_to_twitwicsv(input_filename):
    output_filename = input_filename.replace("ndjson","csv")
    with open(output_filename,"w",encoding="utf-8") as f:    
        writer = csv.writer(f)
        writer.writerow(TWEET_FIELDS)

    ## go through the zs file and write the csv rows
    with open (input_filename,"r",encoding="utf-8") as input_file:
        with open (output_filename,"a",encoding="utf-8") as output_file:
            writer = csv.writer(output_file)
            for line in input_file:
                line_dict_zs = json.loads(line)
                tweets_normalized = normalize_zs_dict(line_dict_zs)
                for tweet in tweets_normalized:
                    csv_row = format_tweet_as_csv_row(tweet)
                    writer.writerow(csv_row)

## -----------------------------------------------------------
## --- code below from https://github.com/medialab/minet -----
## -----------------------------------------------------------
def recombobulate_tweet(tweet_root, entry_id=None):
    __typename = tweet_root["__typename"]

    if __typename == "TweetUnavailable":
        return None

    if __typename == "TweetWithVisibilityResults":
        tweet_root = tweet_root["tweet"]

    try:
        tweet_meta = tweet_root["legacy"]
    except KeyError:
        raise TwitterPublicAPIParsingError(entry_id)

    tweet_meta["source"] = tweet_root["source"]

    # NOTE: tombstone not working anymore
    # if tweet_meta is None:
    #     tweet_meta = getpath(
    #         entry, ["content", "item", "content", "tombstone", "tweet"]
    #     )

    # Skipping ads
    if "promotedMetadata" in tweet_meta:
        return None

    tweet_index = None
    user_index = None

    # NOTE: with new API results we need to build this index each time
    tweet_index = {tweet_meta["id_str"]: tweet_meta}
    user_index = {}

    # Tweet user
    user_index[tweet_meta["user_id_str"]] = tweet_root["core"]["user_results"][
        "result"
    ]["legacy"]

    # Quote
    quoted_root = getpath(tweet_root, ["quoted_status_result", "result"])

    if quoted_root is not None:
        if quoted_root["__typename"] == "TweetWithVisibilityResults":
            quoted_root = quoted_root["tweet"]

        quoted_meta = quoted_root["legacy"]
        quoted_meta["source"] = quoted_root["source"]
        tweet_index[quoted_meta["id_str"]] = quoted_meta
        user_index[quoted_meta["user_id_str"]] = quoted_root["core"]["user_results"][
            "result"
        ]["legacy"]

    for user_str_id, user_meta in user_index.items():
        user_meta["id_str"] = user_str_id

    return process_single_tweet(tweet_meta["id_str"], tweet_index, user_index)

def process_single_tweet(tweet_id, tweet_index, user_index):
    try:
        tweet = tweet_index[tweet_id]
    except KeyError:
        raise TwitterPublicAPIncompleteTweetIndexError(
            tweet_id=tweet_id, tweet_index=tweet_index
        )

    try:
        tweet["user"] = user_index[tweet["user_id_str"]]
    except KeyError:
        raise TwitterPublicAPIncompleteUserIndexError(
            user_id=tweet["user_id_str"], user_index=user_index
        )

    # Quoted?
    quoted_id = tweet.get("quoted_status_id_str")

    # TODO: sometimes tweet is not present
    if quoted_id and quoted_id in tweet_index:
        tweet["quoted_status"] = process_single_tweet(
            quoted_id, tweet_index, user_index
        )

    # Retweeted?
    retweeted_id = tweet.get("retweeted_status_id_str")

    # TODO: sometimes tweet is not present
    if retweeted_id and retweeted_id in tweet_index:
        tweet["retweeted_status"] = process_single_tweet(
            retweeted_id, tweet_index, user_index
        )

    return tweet