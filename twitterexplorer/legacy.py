## =============================================================================
## twitter explorer
## legacy support
## =============================================================================

renamedict = {'created_at_ts':'timestamp_utc',
             'user_id_str':'user_id',
             'user_followers_count':'user_followers',
             'user_friends_count':'user_friends',
             'id_str':'id',
             'in_reply_to_status_id_str':'to_tweetid',
             'in_reply_to_user_id_str':'to_userid',
             'retweeted_status_id_str':'retweeted_id',
             'retweeted_user_id_str':'retweeted_user_id',
             'retweeted_user_screen_name':'retweeted_user',
             'quoted_status_id_str':'quoted_id',
             'quoted_user_id_str':'quoted_user_id',
             'quoted_user_screen_name':'quoted_user',
             'entities_usermentions':'mentioned_ids',
             'entities_hashtags':'hashtags',
             'language':'lang'}

def replace_comma(string):
    if type(string) == str:
        return string.replace(",","|")
    else:
        return string

def convert_to_twitwi(df):
    df = df.rename(columns=renamedict)
    df['mentioned_ids'] = df['mentioned_ids'].apply(replace_comma)
    df['mentioned_names'] = df['mentioned_ids']
    df['hashtags'] = df['hashtags'].apply(replace_comma)    
    return df