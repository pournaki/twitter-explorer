## =============================================================================
## twitter explorer 
## constants
## =============================================================================

cols_to_load = ['id',
                'timestamp_utc',
                'user_screen_name',
                'lang',
                'to_username',
                'to_userid',
                'to_tweetid',
                'user_id',
                'user_name',
                'user_followers', 
                'user_friends',
                'retweeted_id',
                'retweeted_user',
                'retweeted_user_id',
                'quoted_id',
                'quoted_user',
                'quoted_user_id',
                'hashtags',
                'mentioned_names',
                'mentioned_ids',
                'collected_via'
               ]

twitwi_schema = {"id":str,
                 "timestamp_utc":int,
                 "user_screen_name":str,
                 "lang":str,
                 "to_username":str,
                 "to_userid":str,
                 "to_tweetid":str,
                 "user_id":str,
                 "user_name":str,
                 "user_followers":int,
                 "user_friends":int,
                 "retweeted_id":str,
                 "retweeted_user":str,
                 "retweeted_user_id":str,
                 "quoted_id":str,
                 "quoted_user":str,
                 "quoted_user_id":str,
                 "mentioned_ids":str,
                 "mentioned_names":str,                        
                 "hashtags":str,                        
                 }