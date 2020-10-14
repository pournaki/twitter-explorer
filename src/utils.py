import json_lines
from datetime import datetime
import pandas as pd
import altair as alt

def iso_to_string(isostring):
    split = isostring.split("T")
    datetimestring = split[0] + " " + split[1][:5]
    return datetimestring

def tweetjson_to_df(filename):
    tweetlist = []
    with open(filename, 'rb') as f:
        for tweet in json_lines.reader(f):
            tweetdict = {}
            tweetdict["id"] = tweet["id"]
            time = tweet["created_at"]
            tweetdict["time"] = datetime.strptime(
                time, '%a %b %d %X %z %Y').isoformat()
            if 'retweeted_status' in tweet:
                tweetdict["type"] = "retweets"            
            else:
                tweetdict["type"] = "original tweets"
            tweetlist.append(tweetdict)
    tweetdf = pd.DataFrame(tweetlist)
    return tweetdf

def groupby_dates(tweetdf):
    tweetdf["time"] = pd.to_datetime(tweetdf["time"])
    tweetdf = tweetdf.set_index("time")
    grouper = tweetdf.groupby([pd.Grouper(freq='1H'), 'type'])
    result = grouper['type'].count().unstack('type').fillna(0)
    result["datetime"] = result.index
    result["total"] = result["original tweets"] + result["retweets"]
    return result

def plot(grouped_tweetdf):
    # set color range
    domain = ['retweets', 'original tweets','total']
    range_ = ['#1F77B4', '#D62728','grey']

    # plot original tweets and retweets
    C1 = alt.Chart(grouped_tweetdf).mark_area(opacity=0.6).transform_fold(
        fold=['retweets', 'original tweets'], 
        as_=['variable', 'value']
    ).encode(
        alt.X('datetime:T', timeUnit='yearmonthdatehours', title="date"),
        alt.Y('value:Q', stack=None, title="tweet count"),
        color=alt.Color("variable:N",
                        legend=alt.Legend(title="tweet type"),
                        scale=alt.Scale(domain=domain, range=range_),
                         )
    ).properties(width=800, height=500)

    # plot total in background    
    C2 = alt.Chart(grouped_tweetdf).mark_area(opacity=0.15).encode(
        alt.X(f'datetime:T', timeUnit='yearmonthdatehours', title='date'),
        alt.Y('total:Q'),
        color=alt.value("black"))

    return C1+C2    