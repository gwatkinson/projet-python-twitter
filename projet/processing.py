## Process les tweets récupérés


## Import les modules
# Import les modules utilisés
import json
import pandas as pd
import numpy as np
import glob

# Erreurs du projet
import projet.project_errors as errors


## Converti et nettoie les tweets
def folder_to_list_path(folder_path):
    """
    Retourne la liste des fichiers `.json` dans le dossier donné.

    Args:
        folder (str): Chemin du dossier.

    Returns:
        list: Liste des fichiers `.json` dans le dossier.
    """
    list_path = glob.glob(folder_path + "/*.json")

    return list_path


def tweet_json_to_df(list_path):
    """
    Converti les fichiers json en dataframe pandas.

    Args:
        list_path (list): 
            Une liste de `str` qui contiennent les chemin vers les fichiers `.json`.
    
    Returns:
        pandas.dataframe: Dataframe pandas qui contient les tweets.
    """

    # Utiliser une liste de path plutot ?
    # Puis faire une fonction qui renvoie une liste de tous les fichiers json dans un dosiier donné

    assert (
        isinstance(list_path, list) and len(list_path) > 1
    ), "'list_path' doit être une liste"

    # Liste des tweets nettoyés
    tweets_list = []

    # Nettoie et converti les tweets
    print("The file conversion started, this operation can take time")
    for path in list_path:
        with open(path, "r") as fh:
            tweets_json = fh.read().split("\n")

            # Itère sur chaque tweet
            for tweet in tweets_json:
                if tweet:
                    tweet_obj = json.loads(tweet)

                    # Store the user screen name in 'user-screen_name'
                    tweet_obj["user-screen_name"] = tweet_obj["user"]["screen_name"]

                    # Check if this is a 140+ character tweet
                    if "extended_tweet" in tweet_obj:
                        # Store the extended tweet text in 'extended_tweet-full_text'
                        tweet_obj["extended_tweet-full_text"] = tweet_obj[
                            "extended_tweet"
                        ]["full_text"]

                    if "retweeted_status" in tweet_obj:
                        # Store the retweet user screen name in 'retweeted_status-user-screen_name'
                        tweet_obj["retweeted_status-user-screen_name"] = tweet_obj[
                            "retweeted_status"
                        ]["user"]["screen_name"]

                        # Store the retweet text in 'retweeted_status-text'
                        tweet_obj["retweeted_status-text"] = tweet_obj[
                            "retweeted_status"
                        ]["text"]

                        if "extended_tweet" in tweet_obj["retweeted_status"]:
                            tweet_obj[
                                "retweeted_status-extended_tweet-full_text"
                            ] = tweet_obj["retweeted_status"]["extended_tweet"][
                                "full_text"
                            ]

                    if "quoted_status" in tweet_obj:
                        tweet_obj["quoted_status-text"] = tweet_obj["quoted_status"][
                            "text"
                        ]

                        if "extended_tweet" in tweet_obj["quoted_status"]:
                            tweet_obj[
                                "quoted_status-extended_tweet-full_text"
                            ] = tweet_obj["quoted_status"]["extended_tweet"][
                                "full_text"
                            ]

                tweets_list.append(tweet_obj)

    # Create a DataFrame from `tweets_list`
    df_tweets = pd.DataFrame(tweets_list)

    # Drop all the text duplicate (Est ce qu'on a vraiment envie de supprimer les RT ?)
    # df_tweets = df_tweets.drop_duplicates(subset=["text"])

    # Convert the created_at column to np.datetime object
    df_tweets["created_at"] = pd.to_datetime(df_tweets["created_at"])

    # Set the index of df_tweets to id
    df_tweets = df_tweets.set_index("id")

    return df_tweets


def select_time_range(df, start, end):
    """
    Filtre les twwets.
    Garde les tweets créés entre les dates données. 

    Args:
        df (dataframe): La dataframe pandas qui contient les tweets.
        start (str): La date de départ.

            Au format: ``"YYYY-MM-DD HH:MM:SS"``.
        end (str): La date de fin
        
            Au format: ``"YYYY-MM-DD HH:MM:SS"``.

    Returns:
        pandas.dataframe: La dataframe filtrée.

    Examples:
        select_time_range(df, "2020-11-03 08:15:00", "2020-11-03 22:30:00")
    """
    start_time = pd.to_datetime(start, "%Y-%m-%d %H:%M:%S")
    end_time = dt.strptime(end, "%Y-%m-%d %H:%M:%S")
