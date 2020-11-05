### Import les modules ###
import os
import time
import sys
import json
import csv
import numpy as np
import tweepy
from tweepy.streaming import StreamListener


### Authentification et connexion avec l'API ###
class credentials_class:
    def __init__(self, credentials=None):
        """Credentials class

        Classe qui garde les clés de l'API et crée une connexion avec.

        Args:
            credentials (dict, optional):
                Soit un dictionnaire qui contient les clés de l'API.
                Les clés necessaires sont 'consumer_key, 'consumer_secret', 'access_token' et 'bearer_token'.
                Les valeurs sont des chaines de caractères.

                Soit 'None' (par défaut), dans ce cas le fichier local 'twitter_credentials.py' est utilisé.
                Voir 'projet_python_twitter/README.md' pour plus de détails sur 'twitter_credentials.py'. (À compléter)
        
        Attributes:
            consumer_key (str): Contient l'API Key
            consumer_secret (str): Contient l'API Key Secret
            access_token (str): Contient l'Access Token
            access_token_secret (str): Contient l'Access Token Secret
            auth (:obj:`tweepy.OAuthHandler`): Contient l'objet auth de tweepy
                Crée par :func:`~twitter_streaming.credentials_class.authenticate`.
            api (:obj:`tweepy.API`) : Contient l'objet API de tweepy
                Crée par :func:`~twitter_streaming.credentials_class.authenticate`.
        """

        # Attributs clés de l'API
        if credentials is None:
            # Import les clés d'accès de l'API Twitter de `twitter_credentials.py` (à créer localement)
            try:
                import projet_python_twitter.twitter_credentials

                credentials = projet_python_twitter.twitter_credentials.credentials

            except ModuleNotFoundError as e:
                print(
                    "Erreur: " + str(e),
                    "",
                    "Créer le module `twitter_credentials.py` dans ./projet_python_twitter/",
                    "",
                    "De la forme :",
                    "",
                    "credentials = {",
                    "   'consumer_key' : '',",
                    "   'consumer_secret' = '',",
                    "   'access_token' = '',",
                    "   'access_token_secret' = '',",
                    "   'bearer_token' = '' # pas necessaire",
                    "}",
                    sep="\n",
                )

        # Vérifie le format de 'credentials'
        assert type(credentials) is dict
        assert "consumer_key" in credentials
        assert "consumer_secret" in credentials
        assert "access_token" in credentials
        assert "access_token_secret" in credentials

        # Utilise les clés fournies dans le dictionnaire 'credentials'
        self.consumer_key = credentials["consumer_key"]
        self.consumer_secret = credentials["consumer_secret"]
        self.access_token = credentials["access_token"]
        self.access_token_secret = credentials["access_token_secret"]

        # Attributs auth et api
        self.auth, self.api = self.authenticate()

    def authenticate(self):
        """Authentification et connexion à l'API

        Returns:
            (tuple): tuple qui contient :
                auth (:obj:`tweepy.OAuthHandler`): objet OAuthHandler de tweepy qui contient les clés
                api (:obj:`tweepy.API`) : objet api de tweepy qui utilise auth
        """
        auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)
        api = tweepy.API(auth)
        return auth, api


cred = credentials_class()
auth, api = cred.auth, cred.api


class SListener(StreamListener):
    def __init__(self, api=None, fprefix="streamer", path="", max=20000):
        """SListener Class

        Hérite de la classe StreamListener de tweepy.streaming.
        Cette classe permet de gérer comment on traite le stream de Tweet.

        Args:
            api (:obj:`tweepy.API`, optional): L'objet API de tweepy qui gère la connexion avec Twitter.
                C'est le même objet que celui de `credentials_class`
                S'il est omis, il est crée avec 'tweepy.API()'.
            fprefix (str, optional): [description]. Defaults to "streamer".
            path (str, optional): [description]. Defaults to "".
            max (int, optional): [description]. Defaults to 20000.
        """
        self.api = api or tweepy.API()
        self.counter = 0
        self.max = max
        self.fprefix = fprefix
        self.path = path
        self.output = open(
            path + r"%s_%s.json" % (self.fprefix, time.strftime("%Y%m%d-%H%M%S")), "w"
        )

    def on_data(self, data):
        if "in_reply_to_status" in data:
            self.on_status(data)
        elif "delete" in data:
            delete = json.loads(data)["delete"]["status"]
            if self.on_delete(delete["id"], delete["user_id"]) is False:
                return False
        elif "limit" in data:
            if self.on_limit(json.loads(data)["limit"]["track"]) is False:
                return False
        elif "warning" in data:
            warning = json.loads(data)["warnings"]
            print("WARNING: %s" % warning["message"])
            return

    def on_status(self, status):
        self.output.write(status)
        self.counter += 1
        if self.counter >= 20000:
            self.output.close()
            self.output = open(
                self.path
                + r"%s_%s.json" % (self.fprefix, time.strftime("%Y%m%d-%H%M%S")),
                "w",
            )
            self.counter = 0
        return

    def on_delete(self, status_id, user_id):
        print("Delete notice: User %s has deleted the tweet %s" % (user_id, status_id))
        return

    def on_limit(self, track):
        print("WARNING: Limitation notice received, tweets missed: %d" % track)
        return

    def on_error(self, status_code):
        print(sys.stderr, "Encountered error with status code:", status_code)
        return True  # Don't kill the stream
        # print("Stream restarted")

    def on_timeout(self):
        print(sys.stderr, "Timeout...")
        return True  # Don't kill the stream
        # print("Stream restarted")


from tweepy import Stream

# liste des mots à tracker faite par fabien.
liste_1 = [
    "JoeBiden",
    "realDonaldTrump",
    "biden",
    "trump",
    "presidentialelection",
    "presidential",
    "election",
    "electionnight",
    "vote",
    "iwillvote",
    "america",
    "govote",
    "uselection",
    "president",
]

liste_2 = [
    "JoeBiden",
    "realDonaldTrump",
    "biden",
    "trump",
    "presidentialelection",
    "electionnight",
    "iwillvote",
    "govote",
    "uselection",
]

# mathias
liste_3 = [
    "biden",
    "trump",
    "JoeBiden",
    "realDonaldTrump",
]

# wilfried
liste_4 = ["iwillvote", "govote", "uselection", "vote"]

# gabriel
liste_5 = [
    "uselection",
    "president",
    "presidentialelection",
    "presidential",
    "electionnight",
]

## Debut du stream
def start_stream(liste_mot, fprefix="", path=""):
    print(
        "Début du stream, checkez le dossier que vous avez spécifié comme chemin pour le stream",
        "\n",
    )
    while True:
        try:
            # Instantiate the SListener object
            listen = SListener(api, fprefix=fprefix, path=path)
            # Instantiate the Stream object
            stream = Stream(auth, listen)
            # Begin collecting data
            # Ici on stream tous les followers du conseil,
            # pour passer à un stream sur tout twitter et filter avec un hastag donné
            # remplacer l'argument de stream.filter par stream.filter(track= ['premier mot','second mot'])
            # ou bien stream.filter(follow = liste_selected_followers )
            stream.filter(track=liste_mot)
        except:
            print("Pause de 15 min avant le prochain essai de streaming")
            time.sleep(900)
            print("Pause terminée")
            continue


if __name__ == "__main__":
    start_stream(
        liste_mot=liste_5,
        fprefix="liste_5",
        path="C:/Users/gabri/Documents/json_files/",
    )
