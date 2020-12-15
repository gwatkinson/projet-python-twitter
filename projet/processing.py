"""Process les tweets récupérés"""

# Import les modules utilisés
import json
import pandas as pd
import numpy as np
import glob
import re
import us
from geotext import GeoText
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Import les listes de variables
import projet.listes_variables

# Import les utils du projet
import projet.projet_utils as utils

# Download librairie nltk
nltk.download("vader_lexicon", quiet=True)


# Convertit les fichiers json en dataframe
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
    Convertit les fichiers json en dataframe pandas.

    Args:
        path_list (list, optional): Une liste des chemin vers les fichiers `.json`.

        folder (str, optional): Le chemin du dossier qui contient les fichiers `.json`.    
            À terminer avec un `/` ou `\`.

        verbose (bool, optional): `True` pour afficher une barre de progrès et des messages.    
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
                utils.progressBar(
                    j, tweet_total, file=i + 1, total_file=file_total, verbose=verbose
                )
        if verbose:
            print("")

    # Créer une DataFrame à partir de `tweets_list`
    df_tweets = pd.DataFrame(tweets_list)

    return df_tweets


# Nettoie la dataframe
def clean_df(
    df,
    index="id",
    date="created_at",
    verbose=False,
    columns=projet.listes_variables.liste_1,
):
    """
    Fonction pour filtrer et nettoyer la dataframe qui contient les tweets.

    Il s'agit de selectionner les variables (donc garder que certaines colonnes) qui nous interresse
    (text, , les counts, la localisation, on supprime retweeted_status et quoted_status).

    Args:
        df (pandas.dataframe): Une dataframe pandas non filtrée ou nettoyée,
            par exemple celle créée après `tweet_json_to_df`.

        index (str, optional): Nom de la colonne de `df` à mettre en index.    
            Mettre `None` pour ne pas avoir d'index.    
            Par défaut : `id`.

        date (str, optional): Nom de la variable de `df` qui contient la date.    
            Mettre `None` pour ne pas avoir de date.    
            Par défaut : `created_at`.

        verbose (bool, optional): `True` pour afficher une barre de progrès
            et des messages supplémentaires.    
            Par défaut : `False`.

        columns (list, optional): Liste des variables à garder.    
            Voir `projet/listes_variables` pour des exemples de listes.

    Returns:
        pandas.dataframe: Renvoie une dataframe filtrée et nettoyée.
    """
    # Vérifie que toute les variables données existent dans df
    wrong_var = [
        list(var)[0]
        for var in [[index], [date]] + columns
        if var and list(var)[0] not in list(df)
    ]
    if wrong_var:
        raise utils.WrongColumnName(var=wrong_var)

    total = len(columns) + 3

    if verbose:
        print("Le nettoyage a commencé")

    # Initialise la df
    clean_df = pd.DataFrame()

    # Ajoute la date au format datetime
    if date:
        clean_df[date] = pd.to_datetime(df[date])
    utils.progressBar(current=1, total=total, verbose=verbose)

    # Ajoute les variables
    for i, var in enumerate(columns):
        var_name = "-".join(var)
        new_col = df[list(var)[0]]
        for i in range(1, len(var)):
            new_col = [
                new_col[j].get(var[i], np.nan)
                if isinstance(new_col[j], dict)
                else np.nan
                for j in range(len(new_col))
            ]
        clean_df[var_name] = new_col
        utils.progressBar(current=i + 2, total=total, verbose=verbose)

    # Convertit la date de création des accounts
    if "user-created_at" in clean_df:
        clean_df["user-created_at"] = pd.to_datetime(clean_df["user-created_at"])
    utils.progressBar(current=total - 1, total=total, verbose=verbose)

    # Ajoute les index
    if index:
        clean_df = clean_df.set_index(df[index])
    utils.progressBar(current=total, total=total, verbose=verbose)

    if verbose:
        print("")

    return clean_df


# Fonctions pour ajouter des colonnes
def get_full_text(
    df,
    new_var="full_text",
    text_vars=[
        "extended_tweet-full_text",
        "retweeted_status-extended_tweet-full_text",
        "retweeted_status-text",
        "text",
    ],
    drop_vars=True,
):
    """
    Fonction pour ajouter le texte entier et gérer les RT.

    Args:
        df (pandas.dataframe): Une dataframe pandas avec les variables d'intérêt,
            par exemple celle créée après `clean_df`.

        new_var (str, optional): Nom à donner à la variable qui contient le texte entier.    
            Par défaut : `"full_text"`.

        text_vars (list, optional): Liste des variables contenant du texte par ordre de priorité.    
            Par défaut : `["extended_tweet-full_text", "retweeted_status-extended_tweet-full_text",
            "retweeted_status-text", "text"]`.

        drop_vars (bool, optional): Si `True`, supprime les variables dans `text_vars` pour ne garder que la nouvelle variable.    
            Par défaut : `True`.

    Returns:
        pandas.dataframe: Modifie la dataframe d'entrée en ajoutant la colonne de texte et en supprimant les autres colonnes 
            (si `drop_vars=True`) et la renvoie.
    """
    conditions = [(~df[var].isnull()) for var in text_vars]
    choices = [df[var] for var in text_vars]

    df[new_var] = np.select(conditions, choices)

    if drop_vars:
        df.drop(text_vars, axis=1, inplace=True)

    return df


def add_politics(
    df,
    trump_word="(Trump|Donald|realDonaldTrump|republican)",
    biden_word="(Biden|Joe|JoeBiden|democrat)",
    case=False,
    trump_var="contains_trump",
    biden_var="contains_biden",
    text_vars=["full_text", "user-description"],
):
    """
    Fonction pour ajouter une colonne pour Trump et une pour Biden selon leur présence ou non,
    dans le 'full_text' et la description (par défaut).

    Args:
        df (pandas.dataframe): Une dataframe pandas avec une colonne de texte,  
            par exemple celle créée après `get_full_text`.

        trump_word (str, optional): Expression régulière des mots à associer à la présence de Trump dans le tweet.    
            Par défaut : `"(Trump|Donald|realDonaldTrump|republican)"`.

        biden_word (str, optional): Expression régulière des mots à associer à la présence de Trump dans le tweet.    
            Par défaut : `"(Biden|Joe|JoeBiden|democrat)"`.

        case (bool, optional): `True` pour être case sensitive.    
            Par défaut : `False`.

        trump_var (str, optional): Le nom du suffix de la variable qui contient la présence de Trump.    
            Par défaut : `"contains_trump"`.

        biden_var (str, optional): Le nom du suffix de la variable qui contient la présence de Biden.    
            Par défaut : `"contains_biden"`.

        text_vars (list, optional): Liste des variables de textes à regarder.  
            Par défaut : `["full_text", "user-description"]`.

    Returns:
        pandas.dataframe: Modifie la dataframe d'entrée en ajoutant les colonnes de présence ou non
            de Trump et Biden et la renvoie.
    """
    for var in text_vars:
        df[var + "-" + trump_var] = df[var].str.contains(trump_word, case=case)
        df[var + "-" + biden_var] = df[var].str.contains(biden_word, case=case)

    return df


def add_sentiment(
    df,
    text_vars=["full_text", "user-description"],
    sent_var="sentiment",
    compound_var="compound",
    keep_dict=False,
):
    """
    Fonction pour ajouter la ou les colonnes de sentiment analysis (à l'aide de nltk).

    Args:
        df (pandas.dataframe): Une dataframe pandas avec des colonnes de texte,
            par exemple celle créée après `get_full_text`.

        text_vars (list, optional): Liste des variables de textes auquelles ajouter une colonnes de sentiment score.    
            Par défaut : `["full_text", "user-description"]`.

        sent_var (str, optional): Nom à donner à la variable qui contient le dictionnaire du sentiment analysis.    
            Par défaut : `"sentiment"`.

        compound_var (str, optional): Nom à donner à la variable qui contient le compound du sentiment analysis.    
            Par défaut : `"compound"`.

        keep_dict (bool, optional): Si `True`, on ajoute une colonne qui contient le dictionnaire,
            sinon, on garde seulement le compound.    
            Par défaut : `False`.

    Returns:
        pandas.dataframe: Modifie la dataframe d'entrée en ajoutant les colonnes de sentiment analysis et la renvoie.
    """
    sid = SentimentIntensityAnalyzer()

    # Generate sentiment scores
    for var in text_vars:
        new_col = df[var].fillna(value="").apply(sid.polarity_scores)
        if keep_dict:
            df[var + "-" + sent_var] = new_col
        df[var + "-" + sent_var + "-" + compound_var] = new_col.apply(
            lambda s: s.get("compound")
        )

    return df


def sentiment_class(
    df,
    categories=[
        ("tneg", -1, -0.7),
        ("neg", -0.7, -0.2),
        ("neutre", -0.2, 0.2),
        ("pos", 0.2, 0.7),
        ("tpos", 0.7, 1),
    ],
    compound_vars=[
        "full_text-sentiment-compound",
        "user-description-sentiment-compound",
    ],
    class_var="class",
):
    """
    Fonction pour discrétiser la colonne du sentiment compound.

    Args:
        df (pandas.dataframe): Une dataframe pandas avec des colonnes de sentiment compound,
            par exemple celle créée après `add_sentiment`.

        categories (list, optional): Liste pour nommer les classes et les intervalles correspondant.    
            Par défaut : `[("tneg", -1, -0.7), ("neg", -0.7, -0.2), ("neutre", -0.2, 0.2), ("pos", 0.2, 0.7), 
            ("tpos", 0.7, 1)]`.

        compound_vars (list, optional): Liste des variables de compound à classifier.    
            Par défaut : `["full_text-sentiment-compound", "user-description-sentiment-compound"]`.

        class_var (str, optional): Nom du suffixe à donner aux variables qui contiennent les classes de compound.    
            Par défaut : `"class"`.

    Returns:
        pandas.dataframe: Modifie la dataframe d'entrée en ajoutant les classes des sentiment compounds et la renvoie.
    """
    for var in compound_vars:
        conditions = [(df[var].ge(cat[1]) & df[var].lt(cat[2])) for cat in categories]
        choices = [cat[0] for cat in categories]
        df[var + "-" + class_var] = np.select(conditions, choices)

    return df


def add_label(
    df,
    label_var="label",
    trump_var=("full_text-contains_trump", "T"),
    biden_var=("full_text-contains_biden", "B"),
    missing_var="N",
    class_var="full_text-sentiment-compound-class",
):
    """
    Fonction pour ajouter un label selon la présence de Trump et/ou Biden et de la classe du compound.

    Args:
        df (pandas.dataframe): Une dataframe avec les colonnes de présences de Trump, Biden et les classes des compounds.  
            Par exemple celle créée après `add_politics` et `sentiment_class`.

        label_var (str, optional): Nom à donner à la colonne qui contient les labels.  
            Par défaut : `"label"`.

        trump_var (tuple, optional): (Nom de la variable qui contient la présence de Trump, Préfixe si Trump est présent).  
            Par défaut : `("full_text-countains_trump", "T")`.

        biden_var (tuple, optional): (Nom de la variable qui contient la présence de Biden, Préfixe si Biden est présent).  
            Par défaut : `("full_text-countains_biden", "B")`.

        missing_var (str, optional): Préfixe si Trump et Biden ne sont pas présent.  
            Par défaut : `"N"`.

        class_var (str, optional): Nom de la variable qui contient les classes du compound.  
            Par défaut : `"full_text-sentiment-class"`.

    Returns:
        pandas.dataframe: Modifie la dataframe d'entrée en ajoutant les labels et la renvoie.
    """
    conditions = [
        (df[trump_var[0]] & df[biden_var[0]]),
        (df[trump_var[0]] & ~df[biden_var[0]]),
        (~df[trump_var[0]] & df[biden_var[0]]),
        (~df[trump_var[0]] & ~df[biden_var[0]]),
    ]

    choices = [trump_var[1] + biden_var[1], trump_var[1], biden_var[1], missing_var]

    df[label_var] = np.select(conditions, choices) + df[class_var]

    return df


def get_states(df, state_var="state", location_var="user-location"):
    """
    Fonction pour ajouter une colonne contenant l'état de l'user à partir de 'user-location".

    Args:
        df (pandas.dataframe): Une dataframe avec une colonne de texte de location.

        state_var (str, optional): Nom à donner à la nouvelle variable.    
            Par défaut : `"state"`.

        location_var (str, optional): Le nom de la variable de texte où regarder.    
            Par défaut : `"user-location"`.

    Returns:
        pandas.dataframe: Modifie la dataframe d'entrée en ajoutant une colonne pour l'état.
    """
    states = us.STATES
    full_names = [state.name for state in states]
    abbreviation = [state.abbr for state in states]
    state_metaphone = [state.name_metaphone for state in states]
    # capitals = [state.capital for state in states]
    full_list = [full_names, abbreviation, state_metaphone]
    n = len(full_names)
    assert all(len(var) == n for var in full_list)
    regs = ["(" + "|".join(var[i] for var in full_list) + ")" for i in range(n)]

    def _reg2(row):
        if row[location_var]:
            comps = [re.compile(reg) for reg in regs]
            l = [bool(comp.search(row[location_var])) for comp in comps]
            match = np.array(full_names)[l]  # Garde les noms où c'est True
            if len(match) > 0:
                return np.random.choice(match)  # Renvoie un des matchs aléatoirement
        return np.nan

    df[state_var] = df.apply(_reg2, axis=1)

    return df


def get_states1(
    df, location_var="user-location", state_var="state2", coord_var="coord"
):
    """
    Fonction pour ajouter une colonne contenant l'état de l'user à partir de 'user-location".

    Args:
        df (pandas.dataframe): Une dataframe avec une colonne de texte de location.

        text_var (str, optional): Le nom de la variable de texte où regarder.    
            Par défaut : `"user-location"`.

        state_var (str, optional): Nom à donner à la nouvelle variable.    
            Par défaut : `"state"`.

    Returns:
        pandas.dataframe: Modifie la dataframe d'entrée en ajoutant une colonne pour l'état.
    """
    geolocator = Nominatim(timeout=2, user_agent="projet-python-twitter")
    expr = re.compile(", .*, (.*), United States")

    def _reg1(row):
        if row[location_var]:
            places = GeoText(row[location_var])
            lat_lon = []
            for city in places.cities:
                try:
                    loc = geolocator.geocode(city, language="en-US")
                    if loc:
                        l_state = expr.findall(loc.address)
                        if l_state:
                            st = l_state[0]
                        else:
                            st = np.nan
                        lat_lon.append((st, loc.latitude, loc.longitude))
                except GeocoderTimedOut as e:
                    print(f"Error: geocode failed on input {city} with message {e}")
            if lat_lon:
                return lat_lon[int(np.random.randint(len(lat_lon)))]
        return np.nan, np.nan, np.nan

    new_col = df.apply(_reg1, axis=1)
    df[state_var] = [row[0] for row in new_col]
    df[coord_var] = [(row[1], row[2]) for row in new_col]

    return df


# Fonctions pour filtrer la dataframe
def select_time_range(df, start, end, date_var="created_at"):
    """
    Garde les tweets créés entre les dates données. 

    Args:
        df (dataframe): La dataframe pandas qui contient les tweets ainsi qu'une variable datetime.

        start (str): La date de départ.    
            Au format: `` "%Y-%m-%d %H:%M:%S%z"``.

        end (str): La date de fin.    
            Au format: `` "%Y-%m-%d %H:%M:%S%z"``.

        date_var (str, optional): Le nom de la colonne qui contient la date.    
            Par défaut : "created_at".

    Returns:
        pandas.dataframe: La dataframe filtrée par le temps.

    Examples:
        select_time_range(df, "2020-11-03 08:15:00+01:00", "2021-01-03 22:30:00+01:00")
    """
    start_time = pd.to_datetime(start)
    end_time = pd.to_datetime(end)

    filtered_df = df[(start_time < df[date_var]) & (df[date_var] < end_time)]

    return filtered_df


def remove_null(df, var="full_text-sentiment-compound"):
    """
    Filtre la dataframe pour garder les tweets où var est non nulle.

    Args:
        df (pandas.dataframe): La dataframe pandas qui contient les tweets qui contient la variable var.

        var (str, optional): Nom de la variable à évaluer.    
            Par défaut : `"full_text-sentiment-compound"`.

    Returns:
        pandas.dataframe: La dataframe sans valeurs nulles dans var.
    """
    return df[df[var]!=0]


def keep_lang(df, lang_var="lang", language="en"):
    """
    Filtre la dataframe pour garder les tweets dans la langue donnée.

    Args:
        df (pandas.dataframe): La dataframe pandas qui contient les tweets ainsi qu'une variable lang.

        lang_var (str, optional): La variable qui contient la langue du tweet.    
            Par défaut : `"lang"`.

        language (str, optional): La langue à garder.    
            Par défaut : `"en"`.

    Returns:
        pandas.dataframe: La dataframe filtrée par la langue.
    """
    return df[df[lang_var]==language]


def keep_states(df, state_var="state"):
    """
    Filtre la dataframe pour garder les tweets où l'on associe un état.

    Args:
        df (pandas.dataframe): La dataframe pandas qui contient les tweets ainsi qu'une variable state.

        state_var (str, optional): Nom de la variable qui contient l'état.    
            Par défaut : `"state"`.

    Returns:
        pandas.dataframe: La dataframe où tous les tweets ont un état.
    """
    return df[~df[state_var].isnull()]
