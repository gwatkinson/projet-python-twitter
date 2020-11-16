### Process les tweets récupérés ###


### Import les modules ###
# Import les modules utilisés
import json
import pandas as pd
import glob

# Erreurs du projet
import projet.project_errors as errors


### A tweet flattening function ###
def flatten_tweets(path):
    """Flattens out tweet dictionaries so relevant JSON is in a top-level dictionary"""
    tweets_list = []
    with open(path, "r") as fh:
        tweets_json = fh.read().split("\n")

    # Iterate through each tweet
    for tweet in tweets_json:
        if len(tweet) > 0:
            tweet_obj = json.loads(tweet)

            # Store the user screen name in 'user-screen_name'
            tweet_obj["user-screen_name"] = tweet_obj["user"]["screen_name"]

            # Check if this is a 140+ character tweet
            if "extended_tweet" in tweet_obj:
                # Store the extended tweet text in 'extended_tweet-full_text'
                tweet_obj["extended_tweet-full_text"] = tweet_obj["extended_tweet"][
                    "full_text"
                ]

            if "retweeted_status" in tweet_obj:
                # Store the retweet user screen name in 'retweeted_status-user-screen_name'
                tweet_obj["retweeted_status-user-screen_name"] = tweet_obj[
                    "retweeted_status"
                ]["user"]["screen_name"]

                # Store the retweet text in 'retweeted_status-text'
                tweet_obj["retweeted_status-text"] = tweet_obj["retweeted_status"][
                    "text"
                ]

                if "extended_tweet" in tweet_obj["retweeted_status"]:
                    tweet_obj["retweeted_status-extended_tweet-full_text"] = tweet_obj[
                        "retweeted_status"
                    ]["extended_tweet"]["full_text"]

            if "quoted_status" in tweet_obj:
                tweet_obj["quoted_status-text"] = tweet_obj["quoted_status"]["text"]

                if "extended_tweet" in tweet_obj["quoted_status"]:
                    tweet_obj["quoted_status-extended_tweet-full_text"] = tweet_obj[
                        "quoted_status"
                    ]["extended_tweet"]["full_text"]

        tweets_list.append(tweet_obj)
    return tweets_list

