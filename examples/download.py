import datetime as dt
from twitterexplorer.tweetcollector import Collector

## ========================================
## SEARCH TWEETS (API V2)
## ========================================

collector = Collector()

collector.authenticate(api_version="v2_standard",
                       bearer_token="")

collector.set_parameters_v2(search_query="#zib2",
                            sinceid=None,
                            untilid=None,
                            start_time=None,
                            end_time=None,
                            page_limit=None,
                            tweet_limit=None,                          
                            save_csv=True,                          
                            save_full_api_response=False,
                            output_directory="home/twitterexplorer/data/oneweek",
                            custom_save_name=None,
                           )

collector.start()