## =============================================================================
## twitter explorer
## tweet collector
## =============================================================================

import tweepy
import json
import os
import datetime
import time
from twarc.client2 import Twarc2
from twitwi import normalize_tweet
from twitwi import normalize_tweets_payload_v2
from twitwi import format_tweet_as_csv_row
from twitwi.constants import TWEET_FIELDS
import csv

class Collector():

    def __init__(self,streamlit_interface=False):
        self._api_version = None
        self._search_query = None        
        self._client = None
        self._streamlit_interface = streamlit_interface

    def authenticate(self,
                     api_version,
                     bearer_token=None,
                     api_key=None,
                     api_secret_key=None):
        """Connect to the Twitter API

        Parameters:
        self (Collector object)
        api_version (str, any of ["v1_standard","v2_standard","v2_academic_research"]): API version to connect to
        bearer_token (str): twitter bearer token (only for v2)
        api_key (str): twitter api key (only for v1)
        api_secret_key (str): twitter api secret key (only for v1)
        
        Returns:
        self._client (twarc or tweepy client)
        """


        if api_version in ["v2_standard","v2_academic_research"]:
            client = Twarc2(bearer_token=bearer_token)            
        elif api_version == "v1_standard":
            auth = tweepy.AppAuthHandler(api_key, api_secret_key)
            client = tweepy.API(auth,wait_on_rate_limit=True)            
        self._api_version = api_version
        self._client = client

    def set_parameters_v2(self,
                          search_query,
                          sinceid,
                          untilid,
                          start_time,
                          end_time,
                          page_limit,
                          tweet_limit,                          
                          save_csv,                          
                          save_full_api_response,
                          output_directory,
                          custom_save_name,
                           ):
        """Define parameters for the Twitter Search v2

        Parameters:
        self (Collector object)
        search_query (str): Twitter API advanced search query
        sinceid (str): collect tweets from this ID onwards
        untilid (str): collect tweets until this ID         
        start_time (datetime object): collect tweets from this date
        end_time (datetime object): collect tweets until this date
        page_limit (int): number of pages to crawl
        tweet_limit (int): max number of tweets to collect
        save_csv (bool): save twitwi format to csv
        save_full_api_response (bool): save full output to jsonl
        output_directory (str): where to save the tweets
        custom_save_name (str): filename
        
        Returns:
        self (Collector object)
        """    

        self._search_query = search_query
        self._sinceid = sinceid
        self._untilid = untilid
        self._start_time = start_time
        self._end_time = end_time
        self._tweet_limit = tweet_limit        
        self._save_csv = save_csv
        self._save_full_api_response = save_full_api_response
        self._output_directory = output_directory
        self._custom_save_name = custom_save_name
        self._page_limit = page_limit

    def set_parameters_v1(self,
                          search_query,
                          geocode,
                          language,
                          start_time,
                          end_time,
                          sinceid,
                          untilid,
                          result_type,
                          tweet_limit,
                          save_csv,
                          save_full_api_response,
                          output_directory,
                          custom_save_name,
                           ):
        """Define parameters for the Twitter Search v1

        Parameters:
        self (Collector object)
        search_query (str): Twitter API advanced search query
        geocode (str): lon/lat code 
        language (str): ISO language code
        start_time (datetime object): collect tweets from this date
        end_time (datetime object): collect tweets until this date
        sinceid (str): collect tweets from this ID onwards
        untilid (str): collect tweets until this ID 
        result_type (str, any of ['mixed','popular','latest']: apiv1 result type
        tweet_limit (int): max number of tweets to collect
        save_csv (bool): save twitwi format to csv
        save_full_api_response (bool): save full output to jsonl
        output_directory (str): where to save the tweets
        custom_save_name (str): filename
        
        Returns:
        self (Collector object)
        """    
        self._search_query = search_query
        self._sinceid = sinceid
        self._untilid = untilid
        self._geocode = geocode
        self._language = language
        self._start_time = start_time
        self._end_time = end_time
        self._result_type = result_type
        self._tweet_limit = tweet_limit
        self._save_csv = save_csv
        self._save_full_api_response = save_full_api_response
        self._output_directory = output_directory
        self._custom_save_name = custom_save_name

    def start(self):
        """Start the Search
        """
        
        ## define the name of the output file
        if self._custom_save_name == None:
            datetoday = datetime.date.today()
            savesuffix = self._search_query.replace(" ", "_")            
            savename = f"{datetoday}_tweets_{savesuffix}"
        else:
            savename = self._custom_save_name

        if self._streamlit_interface == True:
            import streamlit as st

        output_path = self._output_directory + "/" + savename
        output_path = output_path.replace("//","/")
        self._output_path = output_path
        if not os.path.exists(self._output_directory):
            os.makedirs(self._output_directory)

        if self._save_csv == True:
            message = f"Writing tweets to `{self._output_path}.csv`..."
            if self._streamlit_interface == True:
                st.write(message)
            else:
                print(message)
        if self._save_full_api_response == True:
            message = f"Writing full response of the Twitter API to `{self._output_path}.jsonl`..."
            if self._streamlit_interface == True:
                st.write(message)
            else:
                print(message)

        message = "Collecting..."
        if self._streamlit_interface == True:
            st.write(message)        
        else:
            print(message)

        if self._api_version in ["v2_standard","v2_academic_research"]:
            Collector.run_v2(self)
        elif self._api_version == "v1_standard":
            Collector.run_v1(self)

    def run_v2(self):
        tweet_count = 0
        ## create stopbutton
        if self._streamlit_interface == True:
            stopbutton = st.button("Stop collecting")

        ## we also collect referenced tweets in the CSV
        ## but this can result in a large number of duplicates
        ## we therefore check before writing the CSV if the 
        ## ID has already been collected
        collected_referenced_tweets = []

        if self._api_version == 'v2_standard':
            search_results = self._client.search_recent(query=self._search_query,
                                             max_results=100,
                                             since_id=self._sinceid,
                                             until_id=self._untilid,
                                             start_time=self._start_time,
                                             end_time=self._end_time,                                       
                                             )
        elif self._api_version == 'v2_academic_research':
            search_results = self._client.search_all(query=self._search_query,
                                             max_results=100,
                                             since_id=self._sinceid,
                                             until_id=self._untilid,
                                             start_time=self._start_time,
                                             end_time=self._end_time,                                       
                                             )        

        # if self._save_csv == True:
        #     message = f"Writing tweets to `{self._output_path}.csv`..."
        #     if self._streamlit_interface == True:            
        #         st.write(message)
        #     else:
        #         print(message)
        # if self._save_full_api_response == True:
        #     message = f"Writing full response of the Twitter API to `{self._output_path}.jsonl`..."
        #     if self._streamlit_interface == True:
        #         st.write(message)
        #     else:
        #         print(message)
        # message = "Collecting..."
        # if self._streamlit_interface == True:
        #     st.write("Collecting...")        
        # else:
        #     print(message)

        ## initialize CSV
        if self._save_csv == True:
            if f"{self._output_path}.csv" not in os.listdir(self._output_directory):
                with open (f"{self._output_path}.csv",'w',encoding='utf-8') as o:
                    w = csv.writer(o)
                    w.writerow(TWEET_FIELDS)
        
        for page_idx,page in enumerate(search_results):

            ## normalize tweets
            tweets_normalized = normalize_tweets_payload_v2(page,extract_referenced_tweets=True)
            
            ## write to CSV
            if self._save_csv == True:
                with open (f"{self._output_path}.csv", "a", encoding = "utf-8") as o:
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
            if self._save_full_api_response == True:
                with open (f"{self._output_path}.jsonl", "a", encoding = "utf-8") as f:
                    json.dump(page, f, ensure_ascii=False)
                    f.write("\n")
            
            ## stop it if the user selected a page limit
            if self._page_limit != 0:
                if page_idx + 1 == self._page_limit:
                    message = f"Hit the page limit. Collected `{tweet_count}` tweets."
                    if self._streamlit_interface == True:
                        st.write(message)
                        st.stop()
                    else:
                        print(message)                    
                    break   
                    
            ## stop the collection manually (only in streamlit)
            if self._streamlit_interface == True:
                if stopbutton:
                    st.write("Halting the collection process...")
                    st.write(f"Collected `{tweet_count}` tweets...")
                    ## st.stop does not work with twarc, so we need to kill the process on the system level...
                    # os.kill(pid, signal.SIGKILL)
                    st.stop()

            ## write how many tweets we have so far
            if page_idx != 0 and page_idx % 50 == 0:
                message = f"Collected `{tweet_count}` tweets so far..."
                if self._streamlit_interface == True:
                    st.write(message)
                else:
                    print(message)

            if self._tweet_limit != None and self._tweet_limit != 0:
                if tweet_count >= self._tweet_limit:
                    message =  f"Collected the desired maximum of `{tweet_count}` tweets!"
                    if self._streamlit_interface == True:
                        st.write(message)
                        st.stop()
                    else:
                        print(message)
                    break

        message = f"Done. Collected {tweet_count} tweets."
        if self._streamlit_interface == True:
            st.write(message)
        else:
            print(message)

    def run_v1(self):

        tweet_count = 0
        ## create stopbutton
        if self._streamlit_interface == True:
            stopbutton = st.button("Stop collecting")

        cursor = tweepy.Cursor(self._client.search_tweets,
                                     q=self._search_query,
                                     geocode=self._geocode,
                                     count=100,
                                     tweet_mode='extended',
                                     lang=self._language,
                                     until=self._end_time,
                                     since_id=self._sinceid,
                                     max_id=self._untilid,
                                     result_type=self._result_type).items()
        # initialize csv
        if self._save_csv == True:
            if f"{self._output_path}.csv" not in os.listdir(self._output_directory):
                with open (f"{self._output_path}.csv",'w',encoding='utf-8') as o:
                    w = csv.writer(o)
                    w.writerow(TWEET_FIELDS)        

        while True:
            try:
                tweet = cursor.next()
                tweet_json = (tweet._json)
                                
                if self._start_time != None:
                    # check if the tweet is still within the desired date range
                    tweetdatetime = datetime.datetime.strptime(tweet_json['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
                    if tweetdatetime < self._start_time:
                        message = (f"Collected all the tweets in the desired timerange! Collected {tweet_count} tweets.")
                        if self._streamlit_interface == True:
                            st.write(message)
                            st.stop()
                        else:
                            print(message)
                        break

                    # if yes, write it to file
                    else:
                        tweet_count += 1
                        # tweet_csv = tweetobject_to_csvrow(tweet_json)
                        tweet_normalized = normalize_tweet(tweet_json,collection_source='twitterexplorer')
                        tweet_csv = format_tweet_as_csv_row(tweet_normalized)
                        if self._save_full_api_response == True:
                            with open (f"{self._output_path}.jsonl", "a", encoding = "utf-8") as f:
                                json.dump(tweet_json, f, ensure_ascii=False)
                                f.write("\n")
                        if self._save_csv == True:
                            with open (f"{self._output_path}.csv", "a", encoding = "utf-8") as o:
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
                    if self._save_csv == True:
                        # tweet_csv = tweetobject_to_csvrow(tweet_json)
                        tweet_normalized = normalize_tweet(tweet_json,collection_source='twitterexplorer')
                        tweet_csv = format_tweet_as_csv_row(tweet_normalized)
                        with open (f"{self._output_path}.csv", "a", encoding = "utf-8") as o:
                            writer = csv.writer(o)
                            writer.writerow(tweet_csv)                    
                    if self._save_full_api_response ==True:
                        with open (f"{self._output_path}.jsonl", "a", encoding = "utf-8") as f:
                            json.dump(tweet_json, f, ensure_ascii=False)
                            f.write("\n")
                    del tweet
                    del tweet_normalized
                    del tweet_csv
                    del tweet_json

            # when you attain the rate limit:
            except tweepy.TweepyException:
                message = f"Attained the rate limit. Going to sleep. Collected {tweet_count} tweets."
                # go to sleep and wait until rate limit
                
                if self._streamlit_interface == True:
                    st.write(message)
                    st.write("Sleeping...")
                    my_bar = st.progress(0)
                    for i in range (900):
                        time.sleep(1)
                        my_bar.progress((i+1)/900)
                    st.write("Collecting...")
                else:
                    print(message)
                    print("Sleeping...")
                continue

            # when you collected all possible tweets:
            except StopIteration:
                message = f"Collected all possible {tweet_count} tweets from last week."
                if self._streamlit_interface == True:
                    st.write(message)
                else:
                    print(message)
                break            

            if self._tweet_limit != None and self._tweet_limit != 0:
                if tweet_count >= self._tweet_limit:
                    message =  f"Collected the desired maximum of `{tweet_count}` tweets!"
                    if self._streamlit_interface == True:
                        st.write(message)
                        st.stop()
                    else:
                        print(message)
                    break
