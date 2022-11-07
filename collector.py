## =============================================================================
## twitter explorer collector
## =============================================================================

import streamlit as st
import tweepy
from twarc.client2 import Twarc2
import json
import os
import datetime
import time
import sys
from twitterexplorer.streamlitutils import *
import csv

from twitwi import normalize_tweet
from twitwi import normalize_tweets_payload_v2
from twitwi import format_tweet_as_csv_row
from twitwi.constants import TWEET_FIELDS

ui_changes()

## create data directory
DATADIR = "./data"
if not os.path.exists(DATADIR):
    os.makedirs(DATADIR)

## get the process id
# pid = os.getpid()

st.title("Collector")

st.write("Use the [Twitter Search API](https://developer.twitter.com/en/docs/twitter-api) to collect a set of tweets based on an advanced search query.")

api_type = st.radio(label="Select your API access",
                    options=['Standard API v2','Academic Research API v2','Standard API v1.1 (deprecated soon)'])

if api_type in ['Standard API v2','Academic Research API v2']:

    ## display howto for creating the auth file
    if "twitter_bearertoken.txt" not in os.listdir("./"):

        st.subheader("Authentication")
        st.write("Save your [Twitter bearer token](https://developer.twitter.com/en/docs/authentication/oauth-2-0/bearer-tokens) to `./twitter_bearertoken.txt` in the following format:")

        st.write("""```
        # bearer token
<insert bearer token here>
```""")
        st.stop()
    ## read credentials
    credentials = []
    for line in open("./twitter_bearertoken.txt"):
        li=line.strip()
        if not li.startswith("#"):
            credentials.append(li)    
    a = credentials[0]

    ## authenticate and initialize API
    t = Twarc2(bearer_token=a)

    st.subheader("Keyword search")
    twitter_search_query = st.text_input("Insert your advanced search query here", 
                                         help="Help for creating an advanced search query: https://twitter.com/search-advanced",
                                         value='')

    ## get default timerange for custom date selector
    datetoday = datetime.date.today()
    datelastweek = datetoday - datetime.timedelta(weeks=1)

    with st.expander("Advanced API settings"):
        st.write("")
        sinceid = st.text_input(label="SINCE_ID/ Return statuses with an ID greater than (that is, more recent than) the specified tweet ID.",
                                help="There are limits to the number of Tweets which can be accessed through the API. If the limit of Tweets has occurred since the since_id, the since_id will be forced to the oldest ID available.")
        untilid = st.text_input(label="UNTIL_ID/ Return statuses with an ID less than (that is, older than) or equal to the specified tweet ID.",
                              )
        timerange = st.date_input(label="DATE_RANGE/ Return tweets created in the given time range (including the first and last day).",
                                  help="Keep in mind that the search index has a 7-day limit if you are not using the academic research API: choosing a date earlier than one week past will return no tweets.",
                                  value=[datelastweek,datetoday],
                                  min_value=datetime.date(2016,7,15), # day Twitter was launched
                                  max_value=datetoday
                                  )    
        since_date = timerange[0]
        ## until the full last day
        until_date = timerange[1] + datetime.timedelta(days=1)    

        page_limit = st.number_input(label="PAGE_LIMIT/ Request only the desired number of pages from the API. The API returns 100 results per page. Leave at 0 for all possible results.",format="%i",value=0)

    savesuffix = twitter_search_query.replace(" ", "_")

    if str(timerange[0]) == str(datelastweek) and str(timerange[1]) == str(datetoday) and api_type == "Standard API v2":
        since_date = None
        until_date = None
    else:
        ## add UTC timezone for twarc
        Y0 = since_date.year
        M0 = since_date.month
        D0 = since_date.day
        since_date = datetime.datetime(Y0, M0, D0, 0, 0, 0, 0, datetime.timezone.utc)
        Y1 = until_date.year
        M1 = until_date.month
        D1 = until_date.day
        until_date = datetime.datetime(Y1, M1, D1, 0, 0, 0, 0, datetime.timezone.utc)

    if sinceid == "":
        sinceid = None
    if untilid == "":
        untilid = None

    with st.expander("Advanced saving options"):
        st.write("")
        savename = st.text_input(label="Save name for the collection",
                                 value=f"{datetoday}_tweets_{savesuffix}",
                                 help="Be careful on MS Windows, since you cannot exceed a filename of 259 characters.")
        st.write("")
        save_csv = st.checkbox("Save the tweets as csv for exploration with the twitter-explorer visualizer",
                                help=f"Keep this option checked if you want to save the tweets as smaller files and use the visualizer.",
                                value=True)    
        save_full_api_response = st.checkbox("Save the full response of the Twitter API as json-lines.",
                                             help="Keep this option checked if you want to save the full response of the Twitter API, which results in files ~10 times as large as the csv files.")

        if save_csv == False and save_full_api_response == False:
            st.error("Please choose at least one save option.")

    def tweet_collector():

        tweet_count = 0

        ## we also collect referenced tweets in the CSV
        ## but this can result in a large number of duplicates
        ## we therefore check before writing the CSV if the 
        ## ID has already been collected
        collected_referenced_tweets = []

        if api_type == 'Standard API v2':
            search_results = t.search_recent(query=twitter_search_query,
                                             max_results=100,
                                             since_id=sinceid,
                                             until_id=untilid,
                                             start_time=since_date,
                                             end_time=until_date,                                       
                                             )
        elif api_type == 'Academic Research API v2':
            search_results = t.search_all(query=twitter_search_query,
                                             max_results=100,
                                             since_id=sinceid,
                                             until_id=untilid,
                                             start_time=since_date,
                                             end_time=until_date,                                       
                                             )        

        if save_csv == True:
            st.write(f"Writing tweets to `{DATADIR}/{savename}.csv`...")
        if save_full_api_response == True:
            st.write(f"Writing full response of the Twitter API to `{DATADIR}/{savename}.jsonl`...")
        st.write("Collecting...")        

        ## initialize CSV
        if save_csv == True:
            if f"{DATADIR}/{savename}.csv" not in os.listdir("./data/"):
                with open (f"{DATADIR}/{savename}.csv",'w',encoding='utf-8') as o:
                    w = csv.writer(o)
                    w.writerow(TWEET_FIELDS)
        
        for page_idx,page in enumerate(search_results):

            ## normalize tweets
            tweets_normalized = normalize_tweets_payload_v2(page,extract_referenced_tweets=True)
            
            ## write to CSV
            if save_csv == True:
                with open (f"{DATADIR}/{savename}.csv", "a", encoding = "utf-8") as o:
                    for tweet in tweets_normalized:

                        ## check if the tweet is referenced
                        ## if we have already collected it, 
                        ## then we don't write it to CSV again
                        if 'collected_via' in tweet.keys():
                            if tweet['id'] in collected_referenced_tweets:
                                pass
                            else:                                
                                tweet_csv = format_tweet_as_csv_row(tweet)
                                writer = csv.writer(o)
                                writer.writerow(tweet_csv)                                  
                                collected_referenced_tweets.append(tweet['id'])
                                tweet_count+=1
                        else:
                            tweet_csv = format_tweet_as_csv_row(tweet)
                            writer = csv.writer(o)
                            writer.writerow(tweet_csv)
                            tweet_count+=1        
            
            ## write to jsonl
            if save_full_api_response == True:
                with open (f"{DATADIR}/{savename}.jsonl", "a", encoding = "utf-8") as f:
                    json.dump(page, f, ensure_ascii=False)
                    f.write("\n")
            
            ## stop it if the user selected a page limit
            if page_limit != 0:
                if page_idx + 1 == page_limit:
                    st.write(f"Hit the page limit. Collected `{tweet_count}` tweets.")
                    break   
                    st.stop()

            ## stop the collection manually
            if stopbutton:
                st.write("Halting the collection process...")
                st.write(f"Collected `{tweet_count}` tweets...")
                ## st.stop does not work with twarc, so we need to kill the process on the system level...
                # os.kill(pid, signal.SIGKILL)
                st.stop()

            ## write how many tweets we have so far
            if page_idx != 0 and page_idx % 50 == 0:
                st.write(f"Collected `{tweet_count}` tweets so far...")

    startbutton = st.button("Start collecting")
    if startbutton:        
        stopbutton = st.button("Stop collecting")
        tweet_collector()

## CAUTION
## tweepy's API v1.1 cursor causes RAM overflow on large collections
## it is recommended to use the API v2, which relies on twarc
else:
    if "twitter_apikeys.txt" not in os.listdir("./"):

        st.subheader("Authentication")
        st.write("Save your Twitter credentials to `./twitter_apikeys.txt` in the following format:")

        st.write("""```
        # api_key
        <insert api_key here>
        # api_secret_key
        <insert api_secret_key here>
        ```""")

    # read credentials
    credentials = []
    for line in open("./twitter_apikeys.txt"):
        li=line.strip()
        if not li.startswith("#"):
            credentials.append(li)    
    a = credentials[0]
    b = credentials[1]

    # authenticate and initialize API via AppAuth
    auth = tweepy.AppAuthHandler(a, b)
    api = tweepy.API(auth,wait_on_rate_limit=True)

    st.subheader("Keyword search")
    keywords = st.text_input("Insert keyword(s) here", 
                             help="Search query string of 500 characters maximum, including operators. Queries may additionally be limited by complexity.",
                             value='')

    # get timerange for custom date selector
    datetoday = datetime.date.today()
    datelastweek = datetoday - datetime.timedelta(weeks=1)

    with st.expander("Advanced API settings"):
        st.write("")
        geocode = st.text_input('GEOCODE/ Return tweets by users located within a radius of a given latitude/longitude.',
                                help='The location is preferentially taking from the Geotagging API, but will fall back to their Twitter profile. The parameter value is specified by "latitude,longitude,radius" (without spaces!), where radius units must be specified as either "mi" (miles) or "km" (kilometers). Note that you cannot use the near operator via the API to geocode arbitrary locations; however you can use this geocode parameter to search near geocodes directly. A maximum of 1,000 distinct "sub-regions" will be considered when using the radius modifier. Example: 48.210033,16.363449,100km')
        language = st.text_input("LANGUAGE/ Restrict tweets to the given language, given by an ISO 639-1 code.")    
        sinceid = st.text_input(label="SINCE_ID/ Return only statuses with an ID greater than (that is, more recent than) the specified tweet ID.",
                                help="There are limits to the number of Tweets which can be accessed through the API. If the limit of Tweets has occurred since the since_id, the since_id will be forced to the oldest ID available.")
        maxid = st.text_input(label="MAX_ID/ Return only statuses with an ID less than (that is, older than) or equal to the specified tweet ID.",
                              )
        timerange = st.date_input(label="DATE_RANGE/ Return tweets created in the given time range (including the first and last day).",
                                  help="Keep in mind that the search index has a 7-day limit. In other words, no tweets will be found for a start date older than one week. Furthermore, the Twitter API only allows you to set the upper bound of the date range (until_date). The lower bound is added artificially by stopping the search as soon as the incoming tweet object's date is earlier than the lower bound.",
                                  value=[datelastweek,datetoday])    
        since_date = timerange[0]
        until_date = timerange[1] + datetime.timedelta(days=1)    
        restype = st.radio(label="RESULT_TYPE/ Specifies what type of search results you would prefer to receive.", options=["mixed (include both popular and real time results in the response)", "recent (return only the most recent results in the response)","popular (return only the most popular results in the response)"], index=0)
        restype = restype.split('(')[0][:-1]

    savesuffix = keywords.replace(" ", "_")

    if str(timerange[0]) == str(datelastweek) and str(timerange[1]) == str(datetoday):
        since_date = None
        until_date = None

    if geocode == "":
        geocode = None
    else:
        savesuffix += f"_geo-{geocode}"

    if language == "":
        language = None
    else:
        savesuffix += f"_lang-{language}"

    savesuffix += f"_res-{restype}"

    if sinceid == "":
        sinceid = None
    if maxid == "":
        maxid = None

    with st.expander("Advanced saving options"):
        st.write("")
        savename = st.text_input(label="Save name for the collection",
                                 value=f"{datetoday}_tweets_{savesuffix}",
                                 help="Be careful on MS Windows, since you cannot exceed a filename of 259 characters.")
        st.write("")
        save_csv = st.checkbox("Save the tweets as csv for exploration with the twitter-explorer visualizer",
                                help=f"Keep this option checked if you want to save the tweets as smaller files and use the visualizer.",
                                value=True)    
        save_full_api_response = st.checkbox("Save the full response of the Twitter API as json-lines.",
                                             help="Keep this option checked if you want to save the full response of the Twitter API, which results in files ~10 times as large as the csv files.")

        if save_csv == False and save_full_api_response == False:
            st.error("Please choose at least one save option.")

    if st.button("Start collecting"):

        tweet_count = 0
        if save_csv == True:
            st.write(f"Writing tweets to `{DATADIR}/{savename}.csv`...")
        if save_full_api_response == True:
            st.write(f"Writing full response of the Twitter API to `{DATADIR}/{savename}.jsonl`...")
        st.write("Collecting...")
        c = tweepy.Cursor(api.search_tweets,
                          q=keywords,
                          geocode=geocode,
                          count=100,
                          tweet_mode='extended',
                          lang=language,
                          until=until_date,
                          since_id=sinceid,
                          max_id=maxid,
                          result_type=restype).items()

        # initialize csv
        if save_csv == True:
            if f"{DATADIR}/{savename}.csv" not in os.listdir("./data/"):
                with open (f"{DATADIR}/{savename}.csv",'w',encoding='utf-8') as o:
                    w = csv.writer(o)
                    w.writerow(TWEET_FIELDS)

        while True:
            try:
                tweet = c.next()
                tweet_json = (tweet._json)
                                
                if since_date != None:
                    # check if the tweet is still within the desired date range
                    tweetdatetime = datetime.datetime.strptime(tweet_json['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
                    if tweetdatetime.date() < since_date:
                        st.write(f"Collected all the tweets in the desired timerange! Collected {tweet_count} tweets.")
                        break

                    # if yes, write it to file
                    else:
                        tweet_count += 1
                        # tweet_csv = tweetobject_to_csvrow(tweet_json)
                        tweet_normalized = normalize_tweet(tweet_json,collection_source='twitterexplorer')
                        tweet_csv = format_tweet_as_csv_row(tweet_normalized)
                        with open (f"{DATADIR}/{savename}.jsonl", "a", encoding = "utf-8") as f:
                            json.dump(tweet_json, f, ensure_ascii=False)
                            f.write("\n")
                        with open (f"{DATADIR}/{savename}.csv", "a", encoding = "utf-8") as o:
                            writer = csv.writer(o)
                            writer.writerow(tweet_csv)
                        ## clear variables from RAM
                        del tweet
                        del tweet_normalized
                        del tweet_csv
                        del tweet_json

                # write the tweet
                else:
                    tweet_count += 1
                    if save_csv == True:
                        # tweet_csv = tweetobject_to_csvrow(tweet_json)
                        tweet_normalized = normalize_tweet(tweet_json,collection_source='twitterexplorer')
                        tweet_csv = format_tweet_as_csv_row(tweet_normalized)
                        with open (f"{DATADIR}/{savename}.csv", "a", encoding = "utf-8") as o:
                            writer = csv.writer(o)
                            writer.writerow(tweet_csv)                    
                    if save_full_api_response ==True:
                        with open (f"{DATADIR}/{savename}.jsonl", "a", encoding = "utf-8") as f:
                            json.dump(tweet_json, f, ensure_ascii=False)
                            f.write("\n")
                    del tweet
                    del tweet_normalized
                    del tweet_csv
                    del tweet_json

            # when you attain the rate limit:
            except tweepy.TweepyException:
                st.write(f"Attained the rate limit. Going to sleep. Collected {tweet_count} tweets.")
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
                st.write(f"Collected all possible {tweet_count} tweets from last week.")
                break    