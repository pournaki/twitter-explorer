#!/usr/bin/env python

"""Interactive interface for Twitter Search API.

Connects to Twitter Search API and collects tweets based on keyword.
Saves collected tweets as jsonl in ./data. 
"""

__author__    = "Armin Pournaki"
__copyright__ = "Copyright 2020, Armin Pournaki"
__credits__   = ["Felix Gaisbauer", "Sven Banisch", "Eckehard Olbrich"]
__license__   = "GPLv3"
__version__   = "0.1"
__email__     = "pournaki@mis.mpg.de"

import streamlit as st
import tweepy
import json
import os
import datetime
import time
import sys

# ------- UI --------- #
# Some CSS changes
st.markdown('<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;\
            700&display=swap" rel="stylesheet"> ',
            unsafe_allow_html=True)
st.markdown(
    '<style>.reportview-container .markdown-text-container{font-family:\
    "Inter", -apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica\
     Neue",Arial,sans-serif}\
     #titlelink {color: white;\
     text-decoration: none}\
     #titlelink:hover {color: #cccccc;\
     text-decoration: none}</style>', unsafe_allow_html=True)
st.markdown('<style>.ae{font-family:"Inter",-apple-system,system-ui,BlinkMacSystemFont,\
            "Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif}</style>',
            unsafe_allow_html=True)
st.markdown('<style>body{font-family:"Inter",-apple-system,system-ui,BlinkMacSystemFont,\
            "Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif}</style>',
            unsafe_allow_html=True)
st.markdown('<style>code{color:black}</style>', unsafe_allow_html=True)
st.markdown('<style>.reportview-container .markdown-text-container a{color:rgba\
            (83,106,160,1)}</style>', unsafe_allow_html=True)
st.markdown('<head><title>twitter explorer</title></head>',
            unsafe_allow_html=True)
st.markdown('<p style="font-size: 30pt; font-weight: bold; color: white; \
    background-color: #000">&nbsp;\
    <a id="titlelink" href="https://twitterexplorer.org">twitter explorer\
    <span style="font-size:10pt;">BETA</span></a>\
    </p>', unsafe_allow_html=True)
st.title("Collector")

st.write("Use the [Twitter Search API](https://developer.twitter.com/en/docs/tweets/search/api-reference/get-search-tweets) to collect a set of relevant tweets from the last 7 days based on a keyword search.")

st.subheader("Authentication")
st.write("Save your Twitter credentials to `./twitter_apikeys.txt` in the following format:")

st.write("""```
# api_key
<insert api_key here>
# api_secret_key
<insert api_secret_key here>
```""")

# st.write("""```
# # api_key
# <insert api_key here>
# # api_secret_key
# <insert api_secret_key here>
# # access_token
# <insert access_token here>
# # access_token_secret
# <insert access_token_secret here>
# ```""")

credentials = []
try:
    for line in open("./twitter_apikeys.txt"):
        li=line.strip()
        if not li.startswith("#"):
            credentials.append(li)    
except FileNotFoundError:
    st.error("Please follow the above instructions to use the collector.")

a = credentials[0]
b = credentials[1]
# c = credentials[2]
# d = credentials[3]

# authenticate and initialise api
auth = tweepy.AppAuthHandler(a, b)
# auth.set_access_token(c, d)
api = tweepy.API(auth)

st.subheader("Keyword search")
keywords = st.text_input("Insert keyword(s) here", value='')
savename = keywords.replace(" ", "_")
# create directories before it's too late
datadir = "./data"
if not os.path.exists(datadir):
    os.makedirs(datadir)

datetoday = datetime.date.today()
datelastweek = datetoday - datetime.timedelta(weeks=1)
count = 0
advanced = st.checkbox("Advanced API settings")
if advanced:
    language = st.text_input("Restrict tweets to the given language, given by an ISO 639-1 code (leave empty for all languages)")
    until_date = st.date_input("Collect tweets only until date:", value=datelastweek)
    restype = st.radio(label="Type of result", options=["mixed (include both popular and real time results in the response)", "recent (return only the most recent results in the response)","popular (return only the most popular results in the response)"], index=0)
    restype = restype.split('(')[0]
if st.button("Start collecting"):
    if advanced:
        st.write("Collecting...")
        c = tweepy.Cursor(api.search,q=keywords,rpp=100, tweet_mode='extended', lang=language, until=until_date, result_type=restype).items()

        while True:
            try:
                tweet = c.next()
                tweet = (tweet._json)
                count += 1
                with open (f"{datadir}/{datetoday}_tweets_{savename}.jsonl", "a", encoding = "utf-8") as f:
                    json.dump(tweet, f, ensure_ascii=False)
                    f.write("\n")

            # when you attain the rate limit:
            except tweepy.TweepError:
                st.write(f"Attained the rate limit. Going to sleep. Collected {count} tweets.")
                # go to sleep and wait until rate limit
                st.write("Sleeping...")
                my_bar = st.progress(0)
                for i in range (900):
                    time.sleep(1)
                    my_bar.progress((i+1)/900)
                st.write("Collecting...")
                continue

            # when you collected all possible tweets:
            except StopIteration:
                st.write(f"Collected all possible {count} tweets from last week.")
                break
    else:
        st.write("Collecting...")
        c = tweepy.Cursor(api.search,q=keywords,rpp=100, tweet_mode='extended').items()

        while True:
            try:
                tweet = c.next()
                tweet = (tweet._json)
                count += 1
                with open (f"{datadir}/{datetoday}_tweets_{savename}.jsonl", "a", encoding = "utf-8") as f:
                    json.dump(tweet, f, ensure_ascii=False)
                    f.write("\n")

            # when you attain the rate limit:
            except tweepy.TweepError:
                st.write(f"Attained the rate limit. Going to sleep. Collected {count} tweets.")
                # go to sleep and wait until rate limit
                st.write("Sleeping...")
                my_bar = st.progress(0)
                for i in range (900):
                    time.sleep(1)
                    my_bar.progress((i+1)/900)
                st.write("Collecting...")
                continue

            # when you collected all possible tweets:
            except StopIteration:
                st.write(f"Collected all possible {count} tweets from last week.")
                break
                