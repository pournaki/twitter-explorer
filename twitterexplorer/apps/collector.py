## =============================================================================
## twitter explorer collector streamlit interface
## =============================================================================

import sys
sys.path.append("/Users/ap/git/twitter-explorer/")

import streamlit as st
import tweepy
from twarc.client2 import Twarc2
import json
import os
import datetime
import time
import csv

from twitterexplorer.streamlitutils import *
from twitterexplorer.defaults import *
from twitterexplorer.tweetcollector import Collector
from twitterexplorer.helpers import read_apikeys

from twitwi import normalize_tweet
from twitwi import normalize_tweets_payload_v2
from twitwi import format_tweet_as_csv_row
from twitwi.constants import TWEET_FIELDS

ui_changes()

## get the process id
# pid = os.getpid()

st.title("Collector")

st.write("Use the [Twitter Search API](https://developer.twitter.com/en/docs/twitter-api) to collect a set of tweets based on an advanced search query.")

api_type = st.radio(label="Select your API access",
                    options=['Standard API v2','Academic Research API v2','Standard API v1.1 (deprecated soon)'])

if api_type in ['Standard API v2','Academic Research API v2']:

    if api_type == 'Standard API v2':
        apitype = "v2_standard"
    elif api_type == 'Academic Research API v2':
        apitype = "v2_academic_research"


    ## display howto for creating the auth file
    if read_apikeys(path=DEFAULT_API_KEY_PATH_V2,version="v2") == False:

        st.subheader("Authentication")
        st.write(f"Save your [Twitter bearer token](https://developer.twitter.com/en/docs/authentication/oauth-2-0/bearer-tokens) to `{DEFAULT_API_KEY_PATH_V2}` in the following format:")

        st.write("""```
        # bearer token
<insert bearer token here>
```""")
        st.stop()
    ## read credentials
    bearer_token = read_apikeys(path=DEFAULT_API_KEY_PATH_V2,version="v2")
    
    DATADIR = st.text_input(label="Path to which the tweets will be downloaded",
                            value=DEFAULT_DATA_DIR)

    if not os.path.exists(DATADIR):
        os.makedirs(DATADIR)

    ## authenticate and initialize API
    st.write("---")
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
                                  min_value=datetime.date(2006,7,15), # day Twitter was launched
                                  max_value=datetoday
                                  )    
        since_date = timerange[0]
        ## until the full last day
        until_date = timerange[1] + datetime.timedelta(days=1)    
        tweet_limit = st.number_input(label="TWEET_LIMIT/ Stop the collection after the given number of tweets.",format="%i",value=0)
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

    startbutton = st.button("Start collecting")
    if startbutton:        
        collector = Collector(streamlit_interface=True)
        collector.authenticate(api_version=apitype,
                               bearer_token=bearer_token)

        collector.set_parameters_v2(search_query=twitter_search_query,
                                    sinceid=sinceid,
                                    untilid=untilid,
                                    start_time=since_date,
                                    end_time=until_date,
                                    page_limit=page_limit,
                                    tweet_limit=tweet_limit,                          
                                    save_csv=save_csv,                          
                                    save_full_api_response=save_full_api_response,
                                    output_directory=DATADIR,
                                    custom_save_name=savename,
                                   )
        collector.start()

## CAUTION
## tweepy's API v1.1 cursor causes RAM overflow on large collections
## it is recommended to use the API v2, which relies on twarc
else:
    if read_apikeys(path=DEFAULT_API_KEY_PATH_V1,version="v1") == False:

        st.subheader("Authentication")
        st.write(f"Save your Twitter credentials to `{DEFAULT_API_KEY_PATH_V1}` in the following format:")

        st.write("""```
        # api_key
<insert api_key here>
# api_secret_key
<insert api_secret_key here>
```""")
        st.stop()
    
    DATADIR = st.text_input(label="Path to which the tweets will be downloaded",
                            value=DEFAULT_DATA_DIR)

    if not os.path.exists(DATADIR):
        os.makedirs(DATADIR)

    # read credentials
    api_key,api_secret_key = read_apikeys(path=DEFAULT_API_KEY_PATH_V1,version="v1")

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
        tweet_limit = st.number_input(label="TWEET_LIMIT/ Stop the collection after the given number of tweets.",format="%i",value=0)        
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

        collector = Collector(streamlit_interface=True)

        collector.authenticate(api_version="v1_standard",
                               api_key=api_key,
                               api_secret_key=api_secret_key)

        collector.set_parameters_v1(search_query=keywords,
                                    geocode=geocode,
                                    language=language,
                                    start_time=since_date,
                                    end_time=until_date,
                                    sinceid=sinceid,
                                    untilid=maxid,
                                    result_type=restype,
                                    tweet_limit=tweet_limit,
                                    save_csv=save_csv,
                                    save_full_api_response=save_full_api_response,
                                    output_directory=DATADIR,
                                    custom_save_name=savename,
                                       )

        collector.start()