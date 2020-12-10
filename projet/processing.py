## Process les tweets récupérés


## Import les modules
# Import les modules utilisés
import json
import pandas as pd
import numpy as np
import glob

# Import les listes de variables
import projet.listes_variables

# Utils du projet
import projet.projet_utils as utils


## Convertit et nettoie les tweets
def folder_to_path_list(folder_path):
    r"""
    Retourne la liste des fichiers `.json` dans le dossier donné.

    Args:
        folder_path (str): Chemin du dossier.
        À terminer avec un `/` ou `\`.

    Examples:
        folder_path("path/to/folder")
        folder_path(r"path\to\folder")
    
    Returns:
        list: Liste des fichiers `.json` dans le dossier.
    """
    path_list = glob.glob(folder_path + "*.json")

    return path_list


def tweet_json_to_df(path_list=None, folder=None, verbose=False):
    r"""
    Converti les fichiers json en dataframe pandas.

    Args:
        path_list (list, optional): 
            Une liste des chemin vers les fichiers `.json`.
        folder (str, optional): 
            Le chemin du dossier qui contient les fichiers `.json`.
            
            À terminer avec un `/` ou `\`.
        verbose (bool, optional): 
            `True` pour afficher une barre de progrès et des messages.

            Par défaut : `False`.
    
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

    if verbose:
        print(
            "La conversion des fichiers 'json' a commencé, cela peut prendre du temps"
        )

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
                if verbose:
                    utils.progressBar(j, tweet_total, file=i + 1, total_file=file_total)
        if verbose:
            print("")

    # Créer une DataFrame à partir de `tweets_list`
    df_tweets = pd.DataFrame(tweets_list)

    return df_tweets


def select_time_range(df, start, end, date_var="created_at"):
    """
    Filtre les tweets.
    Garde les tweets créés entre les dates données. 

    Args:
        df (dataframe): La dataframe pandas qui contient les tweets.
        start (str): La date de départ.

            Au format: ``"YYYY-MM-DD HH:MM:SS"``.
        end (str): La date de fin
        
            Au format: ``"YYYY-MM-DD HH:MM:SS"``.
        date_var (str): Le nom de la colonne qui contient la date

    Returns:
        pandas.dataframe: La dataframe filtrée par le temps.

    Examples:
        select_time_range(df, "2020-11-03 08:15:00", "2021-01-03 22:30:00")
    """
    start_time = pd.to_datetime(start, "%Y-%m-%d %H:%M:%S")
    end_time = pd.to_datetime(end, "%Y-%m-%d %H:%M:%S")

    filtered_df = df[start_time < df[date_var] < end_time]

    return filtered_df


def clean_df(
    df,
    index="id",
    date="created_at",
    vars=projet.listes_variables.liste_1,
    extra=None,
    verbose=False,
):
    """
    Fonction pour nettoyer la df qui contient les tweets.

    Il s'agit de selectionner les variables (donc garder que certaines colonnes) qui nous interresse 
    (text, full text, les counts, la localisation, on supprime retweeted_status et quoted_status).
    Il faut peut etre récuperer les counts via l'API (car on récupère les nouveaux tweets et ils n"ont pas encore de likes).
    Il faudra peut etre utiliser des expr reg pour nettoyer les rt.
    Mettre l'option de choisir le timespan.

    Args:
        df (pandas.dataframe): Dataframe non nettoyée qui contient les tweets.
        index (str, optional): 
            Nom de la colonne de `df` à mettre en index.

            Mettre `None` pour ne pas avoir d'index.

            Par défaut : `id`.
        date (str, optional): 
            Nom de la variable de `df` qui contient la date.

            Mettre `None` pour ne pas avoir de date.

            Par défaut : `created_at`.
        vars (list, optional): 

        extra (list, optional): 
            Même format que vars.

            À utiliser pour ajouter des variables à la valeur par défaut de `vars`.
        verbose (bool, optional): 
            `True` pour afficher une barre de progrès et des messages.

            Par défaut : `False`.

    Returns:
        pandas.dataframe: La dataframe nettoyée.
    """
    # Ajoute les extra à la liste des variables
    columns = vars.copy()
    if extra:
        columns.append(extra)

    # Vérifie que toute les variables données existent dans df
    cols = list(df)
    wrong_var = []
    if index and index not in cols:
        wrong_var.append(index)
    if date and date not in cols:
        wrong_var.append(date)
    for var in columns:
        if isinstance(var, list):
            if var[0] not in cols:
                wrong_var.append(var[0])
        elif isinstance(var, str):
            if var not in cols:
                wrong_var.append(var)
    if wrong_var:
        raise utils.WrongColumnName(var=wrong_var)

    if verbose:
        print("Le nettoyage a commencé")
        total = len(columns) + 3

    # Initialise la df avec les index
    clean_df = pd.DataFrame(index=index)
    if verbose:
        utils.progressBar(current=1, total=total)

    # Ajoute la date au format datetime
    if date:
        clean_df[date] = pd.to_datetime(df[date])
    if verbose:
        utils.progressBar(current=2, total=total)

    # Ajoute les variables
    for i, var in enumerate(columns):
        if isinstance(var, list):
            var_name = "-".join(var)
            new_col = df[var[0]]
            for i in range(1, len(var)):
                new_col = [
                    new_col[j].get(var[i]) if new_col[j] else None
                    for j in range(len(new_col))
                ]
            clean_df[var_name] = new_col
        elif isinstance(var, str):
            clean_df[var] = df[var]
        if verbose:
            utils.progressBar(current=3 + i, total=total)

    # Convertit la date de création des accounts
    if "user-created_at" in clean_df:
        clean_df["user-created_at"] = pd.to_datetime(clean_df["user-created_at"])
    if verbose:
        utils.progressBar(current=total, total=total)

    if verbose:
        print("")

    return clean_df


def nlp(df):
    """
    Fonction pour ajouter la ou les colonnes de nlp (à l'aide de nltk ou TextBlob ou les deux)

    Args:
        df ([type]): [description]
    """
    pass
