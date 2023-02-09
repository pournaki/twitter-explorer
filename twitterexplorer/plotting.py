## =============================================================================
## twitter explorer 
## plot functions
## =============================================================================

import altair as alt
import datetime as dt
import pandas as pd
import numpy as np
import math
import json

from twitterexplorer.defaults import *

def find_out_tweet_type(row):
    if type(row['retweeted_id']) == str:
        return 'retweet'
    if type(row['quoted_id']) == str:
        return 'quote'
    if type(row['to_userid']) == str:
        return 'reply'
    else:
        return 'regulartweet'    

def tweetdf_to_timeseries(df,frequency='1H'):
    dfc = df.copy()
    ## don't plot the referenced tweets, they might go back centuries!
    if "collected_via" in dfc.columns and dfc['collected_via'].isna().sum() > 0:
        dfc = dfc[dfc['collected_via'].isna()]
    dfc['type'] = dfc.apply(lambda row: find_out_tweet_type(row), axis=1)
    dfc['ts_dt'] = pd.to_datetime(dfc['timestamp_utc'], unit= 's')    
    dfc = dfc.set_index("ts_dt")
    grouper = dfc.groupby([pd.Grouper(freq=frequency), 'type'])
    result = grouper['type'].count().unstack('type').fillna(0)
    existing_tweettypes = list(result.columns)
    result['total'] = 0
    for tweettype in existing_tweettypes:
        result['total'] += result[tweettype]
    return result

def plot_timeseries(grouped_tweetdf):
    
    grouped_tweetdf["datetime"] = grouped_tweetdf.index

    # get the right order for color plotting
    types = list(grouped_tweetdf.columns)[:-2]
    counts = []
    for t in types:
        counts.append(grouped_tweetdf[t].sum())
    order_idx = np.array(counts).argsort()[::-1]
    order = [types[i] for i in order_idx]

    # set color range
    domain = order.copy()
    domain.append('total')
    range_ = ['#005AB5','#DC3220','#009E73','#ff7f0e','grey']
    
    # plot 
    C1 = alt.Chart(grouped_tweetdf).mark_area(opacity=0.6).transform_fold(
        fold=order,
        as_=['variable', 'value']
    ).encode(
        alt.X('datetime:T', timeUnit='yearmonthdatehours', title="date"),
        alt.Y('value:Q', stack=None, title="tweet count (hourly)"),
        color=alt.Color("variable:N",
                        legend=alt.Legend(title="tweet type"),
                        scale=alt.Scale(domain=domain, range=range_),
                         )
    )

    # plot total in background    
    C2 = alt.Chart(grouped_tweetdf).mark_area(opacity=0.15).encode(
        alt.X(f'datetime:T', timeUnit='yearmonthdatehours', title='date'),
        alt.Y('total:Q'),
        color=alt.value("black"))

    return (C1+C2).configure_axis(
    labelFontSize=12,
    titleFontSize=12,
).configure_legend(titleFontSize=12,labelFontSize=12)

def plot_tweetlanguages(df):
    with open (PACKAGE_DIR+'/languages.json', 'r', encoding='utf-8') as f:
        iso_to_language = json.load(f)
    language_to_iso = {v: k for k, v in iso_to_language.items()}
    langcounts = pd.DataFrame(df.groupby('lang')["id"].count()).reset_index().rename(columns={'id':'tweet count','lang':'language_code'}).sort_values(by='tweet count', ascending=False)        
    langcounts['language'] = langcounts['language_code'].apply(lambda x: iso_to_language[x])
    langcounts_plot = langcounts.copy()
    langcounts_plot = langcounts_plot[:10].rename(columns={'language':'language (top 10)'})
    langbars = alt.Chart(langcounts_plot).mark_bar().encode(
        y=alt.Y('language (top 10):N', sort='-x'),
        x='tweet count',
        color=alt.Color('language (top 10):N', 
                        scale=alt.Scale(scheme='tableau10'),
                        legend=None)
    ).configure_axis(
    labelFontSize=12,
    titleFontSize=12)    
    return langbars