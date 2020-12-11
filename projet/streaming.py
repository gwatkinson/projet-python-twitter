"""Module pour récupèrer les tweets avec l'API Twitter"""

# Import les modules utilisés
import time
import sys
import json
import tweepy

# Import les erreurs du projet
import projet.projet_utils as utils


# Authentification et connexion avec l'API
class CredentialsClass:
    def __init__(self, credentials, **kwargs):
        """
        Classe qui stock les clés et crée une connexion avec l'API.

        Args:
            credentials: 
                Un dictionnaire qui contient les clés de l'API.

                Les clés necessaires sont `consumer_key`, `consumer_secret`, 
                `access_token` et `bearer_token`.    
                Les valeurs sont des chaines de caractères.

                Voir `projet/README.md` pour un exemple.

            **kwargs (optional): Arguments à passer à `tweepy.API`.

                Voir [la documentation de tweepy](http://docs.tweepy.org/en/latest/api.html#tweepy-api-twitter-api-wrapper)

        Attributes:
            consumer_key (str): Contient l'API Key.
            consumer_secret (str): Contient l'API Key Secret.
            access_token (str): Contient l'Access Token.
            access_token_secret (str): Contient l'Access Token Secret.
            auth: 
                Contient l'objet auth de `tweepy.OAuthHandler`.

                Crée par `CredentialsClass.authenticate`.

            api: 
                Contient l'objet `tweepy.API`.

                Crée par `CredentialsClass.authenticate`.
        """

        # Vérifie le format de 'credentials'
        if type(credentials) is not dict:
            raise utils.CredentialsType(type=type(credentials))

        # Liste des clés nécessaire
        key_names = [
            "consumer_key",
            "consumer_secret",
            "access_token",
            "access_token_secret",
        ]

        # Vérifie si les clés existent bien
        missing_keys = [key for key in key_names if key not in credentials]
        if missing_keys:
            raise utils.MissingKey(missing_keys=missing_keys)

        # Vérifie le type des clés
        wrong_keys = [key for key in key_names if type(credentials[key]) is not str]
        if wrong_keys:
            raise utils.CredentialsKeyType(wrong_keys=wrong_keys)

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


# Stream des Tweets
class SListener(tweepy.StreamListener):
    def __init__(
        self,
        credentials,
        nb=0,
        timeout=None,
        fprefix="streamer",
        path="",
        max=20000,
        verbose=False,
        start=None,
    ):
        """
        Classe qui crée le stream de Tweets et gère l'enregistrement des Tweets récupérés.

        Hérite de la classe `StreamListener` de `tweepy.streaming`.

        Chaque Tweet est enregistré au format `.json`.    
        Puis les tweets sont rassemblés dans des fichiers `.json` de la forme:    
        `[fprefix]_YYYYmmdd-HHMMSS.json`.

        Args:
            credentials: 
                Instance de `CredentialsClass` qui gère la connexion avec l'API de Twitter.
            nb (int, optional): 
                Nombre de tweets à récupérer.

                Mettre 0 (ou un nombre négatif) pour ne pas avoir de limite.

                Par défaut : `0`.
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
            start (float): 
                Contient l'heure du début du stream.

                Par défaut : `None`

        Attributes:
            api: 
                Contient l'objet `tweepy.API`.

                Attribut de `credentials`.
            nb (int): Contient le nombre tweets à récupérer.
            counter (int): Compteur du nombre de tweets dans le fichier actuel.
            nb_tweets (int): Compteur du nombre total de tweets.
            max (int): Contient le nombre maximal de tweets par fichier.
            start (float): Contient l'heure du début du stream.
            timeout (float): Contient la durée du stream.
            fprefix (str): Contient le préfixe.
            path (str): Contient le chemin du dossier.
            output (str): 
                Contient le chemin du fichier actuel.

                Au format: `[path][fprefix]_YYYYmmdd-HHMMSS.json`.
            verbose (bool): Contient la valeur du booléen `verbose`.
        """
        if not isinstance(credentials, CredentialsClass):
            raise utils.CredentialsClassType(type=type(credentials))

        self.api = credentials.api
        self.nb = int(nb) if nb > 0 else 0
        self.nb_tweets = 0
        self.counter = 0
        self.max = int(max) if max > 0 else 0
        self.timeout = timeout
        assert timeout is None or start, "Donner le début du stream"
        self.start = start
        self.verbose = verbose
        self.fprefix = fprefix
        if path:
            assert path[-1] in ["/", "\\"], "'path' doit terminer par '/' ou '\\'."
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
        elif "warning" in data:
            warning = json.loads(data)["warnings"]
            print("WARNING: %s" % warning["message"])
            return

    def on_status(self, status):
        self.output.write(status)
        self.counter += 1
        self.nb_tweets += 1

        if self.verbose:
            if self.nb:
                utils.progressBar(
                    current=self.nb_tweets, total=self.nb, verbose=self.verbose
                )
            elif self.counter % 100 == 0:
                print(["|", "/", "-", "\\"][self.counter // 100 % 4], end="\r")

        if self.nb and self.nb_tweets >= self.nb:
            print("")
            print(f"Les {self.nb} tweets ont été récupérés.")
            raise KeyboardInterrupt

        if self.timeout and time.time() > self.start + self.timeout * 3600:
            print("Durée terminée")
            raise KeyboardInterrupt

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

    def on_timeout(self):
        print(sys.stderr, "Timeout...")
        return True  # Don't kill the stream


def start_stream(
    liste_mots,
    credentials,
    nb=0,
    timeout=None,
    fprefix="streamer",
    path="",
    verbose=False,
):
    r"""
    Cette fonction lance le stream pour la durée donnée.

    Si `timeout` n'est pas défini, le stream est lancé indéfiniment 
    et il faut l'arrêter manuellement.

    Les arguments `fprefix`, `path` et `verbose` sont passés 
    dans une instance de la classe `SListener`.

    Args:
        liste_mots (list): 
            Liste des mots à tracker.

            Doit contenir des `str`.
        credentials: 
            Instance de `CredentialsClass` qui gère la connexion avec Twitter.
        nb (int, optional): 
            Nombre de tweets à récupérer.

                Mettre 0 (ou un nombre négatif) pour ne pas avoir de limite.

                Par défaut : `0`.
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

            Doit finir avec `/` ou `\` si différent de `""`.

            Par défaut : `""`.
        verbose (bool, optional): 
            Si `True`, affiche un point tout les 50 tweets traités ou une barre de progression si `nb>0`.

            Par défaut : `False`.
    """
    wrong_words = [mot for mot in liste_mots if type(mot) is not str]
    if wrong_words:
        raise utils.WordType(wrong_words=wrong_words)

    if not isinstance(credentials, CredentialsClass):
        raise utils.CredentialsClassType(type=type(credentials))

    start = time.time()

    print("Début du stream")

    while True:
        try:
            # Instantiate the SListener object
            listen = SListener(
                credentials,
                fprefix=fprefix,
                path=path,
                verbose=verbose,
                start=start,
                timeout=timeout,
                nb=nb,
            )
            # Instantiate the Stream object
            stream = tweepy.Stream(credentials.auth, listen)
            # Begin collecting data
            stream.filter(track=liste_mots)
        except Exception as e:
            print("")
            print(sys.stderr, "Erreur: " + str(e))
            print("Pause de 15 min avant le prochain essai de streaming")
            time.sleep(300)
            for i in range(1, 3):
                print("Il reste %s min" % (15 - 5 * i))
                time.sleep(300)
            print("Pause terminée")
            continue
        except KeyboardInterrupt:
            print(
                "Le stream a duré : "
                + str(round((time.time() - start) / (60 * 60), 2))
                + "h"
            )
            print("Fin du stream")
            return


# Lancement du stream
if __name__ == "__main__":
    try:
        import projet.listes_mots as listes
        import projet._credentials as _credentials

    except ModuleNotFoundError as e:
        print(
            "Erreur : " + str(e),
            "",
            "Vérifier que '_credentials.py' existe bien et est dans le bon dossier ('projet/')",
            sep="\n",
        )

    else:
        import argparse

        parser = argparse.ArgumentParser(description="Demarre le stream.")
        parser.add_argument("-n", "--nb", type=int, help="Le nombre maximal de tweets.")
        parser.add_argument(
            "-t", "--timeout", type=float, help="Le temps maximal du stream.",
        )
        parser.add_argument(
            "-q",
            "--quiet",
            dest="verbose",
            action="store_false",
            help="Affichage réduit.",
        )
        parser.add_argument(
            "-p",
            "--path",
            default="./data/json/",
            help="Le dossier où enregistrer les fichiers.",
        )
        parser.add_argument(
            "-l",
            "--liste",
            required=True,
            type=int,
            choices=list(range(len(listes.listes_mots))),
            help="Le numero de la liste de 'listes_mots' à utiliser.",
        )
        parser.add_argument("--prefix", help="Le prefix du noms des fichiers.")
        args = parser.parse_args()

        credentials = CredentialsClass(_credentials.credentials)

        start_stream(
            credentials=credentials,  # Vérifier que '_twitter_credentials" existe bien
            liste_mots=listes.listes_mots[
                args.liste
            ],  # Liste de mots à tracker (voir `projet.listes_mots`)
            nb=args.nb,  # Nombre de tweets à recupérer
            timeout=args.timeout,  # Temps maximal du stream
            fprefix=args.prefix
            if args.prefix
            else "liste_"
            + str(args.liste),  # À modifier en fonction de la liste selectionnée
            path=args.path,  # À modifier selon l'utilisateur
            verbose=args.verbose,  # Selon les préférences
        )

