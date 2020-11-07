### Import les modules ###
import os
import time
import sys
import json
import csv
import numpy as np
import tweepy
from tweepy.streaming import StreamListener
from tweepy import Stream


### Authentification et connexion avec l'API ###
class credentials_class:
    def __init__(self, credentials, **kwargs):
        """
        Classe qui stock les clés et crée une connexion avec l'API.

        Args:
            credentials: 
                Un dictionnaire qui contient les clés de l'API.

                Les clés necessaires sont `consumer_key`, `consumer_secret`, 
                `access_token` et `bearer_token`.    
                Les valeurs sont des chaines de caractères.

                Voir `projet_python_twitter/README.md` pour un exemple.

            **kwargs: Arguments à passer à `tweepy.API`.
                Voir [la documentation de tweepy](http://docs.tweepy.org/en/latest/api.html#tweepy-api-twitter-api-wrapper)

        Attributes:
            consumer_key (str): Contient l'API Key.
            consumer_secret (str): Contient l'API Key Secret.
            access_token (str): Contient l'Access Token.
            access_token_secret (str): Contient l'Access Token Secret.
            auth: 
                Contient l'objet auth de `tweepy.OAuthHandler`.

                Crée par `credentials_class.authenticate`.

            api: 
                Contient l'objet `tweepy.API`.

                Crée par `credentials_class.authenticate`.
        """

        # Vérifie le format de 'credentials'
        assert type(credentials) is dict, "'credentials' doit être un dictionnaire"
        assert (
            "consumer_key" in credentials
        ), "Il manque 'consumer_key' dans le dictionnaire"
        assert (
            "consumer_secret" in credentials
        ), "Il manque 'consumer_secret' dans le dictionnaire"
        assert (
            "access_token" in credentials
        ), "Il manque 'access_token' dans le dictionnaire"
        assert (
            "access_token_secret" in credentials
        ), "Il manque 'access_token_secret' dans le dictionnaire"

        # Utilise les clés fournies dans le dictionnaire 'credentials'
        self.consumer_key = credentials["consumer_key"]
        self.consumer_secret = credentials["consumer_secret"]
        self.access_token = credentials["access_token"]
        self.access_token_secret = credentials["access_token_secret"]
        self.kwargs = kwargs
        # Attributs auth et api
        self.auth, self.api = self.authenticate()

    def authenticate(self):
        """
        Authentification et connexion à l'API.

        Returns: 
            Un tuple qui contient :             
                auth: Objet `tweepy.OAuthHandler` qui contient les clés.    
                api: Objet `tweepy.API` qui utilise auth.
        """
        auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)
        api = tweepy.API(auth, self.kwargs)
        return auth, api


### Stream des Tweets ###
class SListener(StreamListener):
    def __init__(
        self, credentials, fprefix="streamer", path="", max=20000, verbose=False
    ):
        """
        Classe qui crée le stream de Tweets et gère l'enregistrement des Tweets récupérés.

        Hérite de la classe `StreamListener` de `tweepy.streaming`.
        
        Chaque Tweet est enregistré au format `.json`.    
        Puis les tweets sont rassemblés dans des fichiers `.json` de la forme:    
        `[fprefix]_YYYYmmdd-HHMMSS.json`

        Args:
            credentials: 
                Instance de `credentials_class` qui gère la connexion avec l'API de Twitter.

            fprefix (str, optional): 
                Préfixe à mettre dans le fichier où les tweets sont enregistrés devant la date. 
                
                Par défaut : `"streamer"`.

            path (str, optional): 
                Chemin du doossier où enregistrer les fichiers.

                Doit finir avec `/` ou `\\` si différent de `""`.

                Par défaut : `""`.

            max (int, optional): 
                Nombre maximal de tweets par fichier.

                Un nouveau fichier est créé une fois la limite atteinte.

                Mettre 0 (ou un nombre négatif) pour ne pas avoir de limite.

                Par défaut : `20000`.

            verbose (bool, optional): 
                Si `True`, affiche un point tout les 50 tweets traités.

                Par défaut : `False`.
        
        Attributes:
            api: 
                Contient l'objet `tweepy.API`.

                Attribut de `credentials`.
            
            counter (int): Compteur du nombre de tweets dans le fichier actuel.
            max (int): Contient le nombre maximal de tweets par fichier.
            fprefix (str): Contient le préfixe.
            path (str): Contient le chemin du dossier.
            output (str): 
                Contient le chemin du fichier actuel.

                Au format: `[path][fprefix]_YYYYmmdd-HHMMSS.json`.

            verbose (bool): Contient la valeur du booléen `verbose`.
        """
        assert isinstance(
            credentials, credentials_class
        ), "'credentials' doit être une instance de 'credentials_class'."
        self.api = credentials.api
        self.counter = 0
        self.max = int(max) if max > 0 else 0
        self.verbose = verbose
        self.fprefix = fprefix
        if len(path) > 0:
            assert path[-1] in ["/", "\\"], "'path' devrait terminer par '/' ou '\\'."
        self.path = path
        self.output = open(
            self.path + self.fprefix + "_" + time.strftime("%Y%m%d-%H%M%S") + ".json",
            "w",
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
        # elif "error" in data:
        #     status_code = json.loads(data)["error"]["status_code"]
        #     if self.on_error(status_code) is False:
        #         return False
        elif "warning" in data:
            warning = json.loads(data)["warnings"]
            print("WARNING: %s" % warning["message"])
            return

    def on_status(self, status):
        self.output.write(status)
        self.counter += 1
        if self.verbose and self.counter % 50 == 0:
            print("|")
        if self.counter >= 20000:
            self.output.close()
            self.output = open(
                self.path
                + self.fprefix
                + "_"
                + time.strftime("%Y%m%d-%H%M%S")
                + ".json",
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
        # if status_code = 420:
        #    time
        # print("Stream restarted")

    def on_timeout(self):
        print(sys.stderr, "Timeout...")
        return True  # Don't kill the stream
        # print("Stream restarted")


def start_stream(
    liste_mot, credentials, timeout=None, fprefix="streamer", path="", verbose=False
):
    """
    Cette fonction lance le stream pour la durée donnée.

    Si `timeout` n'est pas défini, le stream est lancé indéfiniment 
    et il faut l'arrêter manuellement.

    Les arguments `fprefix`, `path` et `verbose` sont passés 
    dans une instance de la classe `SListener`.

    Args:
        liste_mot (list): 
            Liste des mots à tracker.
            
            Doit contenir des `str`.

        credentials: 
            Instance de `credentials_class` qui gère la connexion avec Twitter.

        timeout (float, optional): 
            Le temps (en heures) que le stream doit-il être lancé.

            Si `timeout` est omis, le stream sera lancé indéfiniment 
            et il faudra l'arrêter manuellement.

            C'est le cas par défaut.

        fprefix (str, optional): 
            Préfixe à mettre dans le fichier où les tweets sont enregistrés devant la date.

            Par défaut : `"streamer"`.

        path (str, optional): 
            Chemin du doossier où enregistrer les fichiers.

            Doit finir avec `'/'` ou `'\\'` si différent de `""`.

            Par défaut : `""`.

        verbose (bool, optional): 
            Si `True`, affiche un point tout les 50 tweets traités.

            Par défaut : `False`.
    """
    start_time = end_time = time.time()
    if type(timeout) is float:
        end_time += timeout * 60 * 60

    assert type(liste_mot) is list and all(
        type(mot) is str for mot in liste_mot
    ), "'liste_mot' doit être une liste de string."
    assert isinstance(
        credentials, credentials_class
    ), "'credentials' doit être une instance de 'credentials_class'."

    print(
        "Début du stream, checkez le dossier que vous avez spécifié comme chemin pour le stream"
    )
    while True:
        try:
            # Instantiate the SListener object
            listen = SListener(credentials, fprefix=fprefix, path=path, verbose=verbose)
            # Instantiate the Stream object
            stream = Stream(credentials.auth, listen)
            # Begin collecting data
            stream.filter(track=liste_mot)
        except Exception as e:
            if timeout is not None and time.time() > end_time:
                print(
                    "Le stream a duré :"
                    + str(round((time.time() - start_time) / (60 * 60), 3))
                    + "h"
                )
                print("Fin du stream")
                return
            print(sys.stderr, "Erreur: " + str(e))
            print("Pause de 15 min avant le prochain essai de streaming")
            time.sleep(300)
            for i in range(1, 3):
                print("Il reste %s min" % (15 - 5 * i))
                time.sleep(300)
            print("Pause terminée")
            continue
        except KeyboardInterrupt:
            print("Stream coupé manuellement")
            print(
                "Le stream a duré :"
                + str(round((time.time() - start_time) / (60 * 60), 3))
                + "h"
            )
            print("Fin du stream")
            return


### Lancement du stream ###
if __name__ == "__main__":
    import listes_mots as listes
    import _twitter_credentials

    credentials = credentials_class(_twitter_credentials.credentials)

    start_stream(
        credentials=credentials,  # Vérifier que '_twitter_credentials" existe bien.
        liste_mot=listes.liste_5,  # Liste de mot à tracker (voir `projet_python_twitter.listes_mots`).
        timeout=0.001,
        fprefix="liste_5",  # À modifier en fonction de la liste selectionnée.
        path="C:/Users/gabri/Documents/json_files/",  # À modifier selon l'utilisateur.
        verbose=True,  # Selon les préférences.
    )
