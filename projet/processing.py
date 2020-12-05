## Process les tweets récupérés


## Import les modules
# Import les modules utilisés
import json
import pandas as pd
import numpy as np
import glob

# Erreurs du projet
import projet.project_errors as errors

# Affichage du progrès
def progressBar(current, total, file=None, total_file=None, barLength=20):
    percent = float(current) * 100 / total
    arrow = "-" * int(percent / 100 * barLength - 1) + ">"
    spaces = " " * (barLength - len(arrow) - 1)
    prefix = (
        f"File {file}/{total_file}"
        if file is not None and total_file is not None
        else "Progress"
    )
    print(f"{prefix}: [{arrow}{spaces}] {percent:.0f} %", end="\r")


## Converti et nettoie les tweets
def folder_to_path_list(folder_path):
    """
    Retourne la liste des fichiers `.json` dans le dossier donné.

    Args:
        folder_path (str): Chemin du dossier.
        Ne pas terminer avec un ``/`` ou ``\``.

    Examples:
        folder_path("path/to/folder")
        folder_path("path\\to\\folder")
    
    Returns:
        list: Liste des fichiers `.json` dans le dossier.
    """
    path_list = glob.glob(folder_path + "/*.json")

    return path_list


def tweet_json_to_df(path_list=None, folder=None):
    """
    Converti les fichiers json en dataframe pandas.

    Args:
        path_list (list, optional): 
            Une liste des chemin vers les fichiers `.json`.
        folder (str, optional): 
            Le chemin du dossier qui contient les fichiers `.json`.
            Ne pas terminer avec un ``/`` ou ``\``.
    
    Returns:
        pandas.dataframe: Dataframe pandas qui contient les tweets.
    """
    assert path_list is not None or folder is not None, "Un argument est nécessaire"
    assert path_list is None or (
        path_list
        and isinstance(path_list, list)
        and all(isinstance(path, str) for path in path_list)
    ), "'path_list' doit être une liste de strings"
    assert folder is None or isinstance(
        folder, str
    ), "'folder' doit être une chaîne de caractères"

    if path_list is None:
        path_list = folder_to_path_list(folder_path=folder)

    print("The file conversion started, this operation can take time")

    # Contient la liste des tweets en json
    tweets_list = []
    file_total = len(path_list)
    for i, path in enumerate(path_list):
        with open(path, "r") as fh:
            tweets_json = fh.read().split("\n")
            for j, tweet in enumerate(tweets_json):
                tweet_total = len(tweets_json)
                if tweet:
                    tweet_obj = json.loads(tweet)
                tweets_list.append(tweet_obj)
                progressBar(j, tweet_total, file=i + 1, total_file=file_total)
        print("")

    # Créer une DataFrame à partir de `tweets_list`
    df_tweets = pd.DataFrame(tweets_list)

    # # Store the user screen name in 'user-screen_name'
    # df_tweets["user-screen_name"] = df_tweets["user"]["screen_name"]

    # # Check if this is a 140+ character tweet
    # if "extended_tweet" in df_tweets:
    #     # Store the extended tweet text in 'extended_tweet-full_text'
    #     df_tweets["extended_tweet-full_text"] = df_tweets["extended_tweet"]["full_text"]

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
        select_time_range(df, "2020-11-03 08:15:00", "2021-01-03 22:30:00")
    """
    start_time = pd.to_datetime(start, "%Y-%m-%d %H:%M:%S")
    end_time = pd.to_datetime(end, "%Y-%m-%d %H:%M:%S")

    filtered_df = df[start_time < df["created_at"] < end_time]

    return filtered_df


def filter_df(df):
    """
    Fonction pour filtrer la df qui contient les tweets.

    Il s'agit de selectionner les variables (donc garder que certaines colonnes) qui nous interresse 
    (text, full text, les counts, la localisation, on supprime retweeted_status et quoted_status).
    Il faut peut etre récuperer les counts via l'API (car on récupère les nouveaux tweets et ils n"ont pas encore de likes).
    Il faudra peut etre utiliser des expr reg pour nettoyer les rt.
    Mettre l'option de choisir le timespan.

    Args:
        df ([type]): [description]
    """
    pass


def nlp(df):
    """
    Fonction pour ajouter la ou les colonnes de nlp (à l'aide de nltk ou TextBlob ou les deux)

    Args:
        df ([type]): [description]
    """
    pass
