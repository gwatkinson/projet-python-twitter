# ## Récupération de la liste des followers sélectionnés par le Bureau du Conseil.

# import pandas as pd
# # Mettre en argument le chemin où est enregistré la liste des followers confectionnée par Kevin.
# path_followers = "/Users/mathias/Desktop/Copy-of-WWCfollowersinfo-1-revKC.csv"
# print("La liste des followers enregistré par Kévin est situé à:",path_followers )
# followers = pd.read_csv(path_followers)
# if 'Unnamed: 0' in followers.columns.values:
#     del(followers['Unnamed: 0'])#supprime l'ancien index
# print(followers.head()) #montre les 5 premieres lignes du tableau
# print('\n','----------------------------------------------','\n')


# liste_selected_followers = [] # contiendra la liste des tweets à suivre.
# for i in range(followers.shape[0]):
#     if followers.iloc[i,followers.shape[1]-1]=='Y': #j'assume ici que la colonne 'Important' est la dernière des colonnes
#         liste_selected_followers.append(str(int(followers['follower_id'][i])))

# for i in range(len(liste_selected_followers)):
#     liste_selected_followers[i]=str(liste_selected_followers[i])
# print('number of selected followers :',len(liste_selected_followers))
# print('\n','----------------------------------------------','\n')
# print('5 first id of the selected followers', '\n', liste_selected_followers[:5])

###
# import the modules
import tweepy

# Code pour l'installation du module tweepy (plus rarement déjà téléchargé)
# import pip
# package_name='tweepy'
# pip.main(['install',package_name])
import json
import time
import sys
import os
import csv
import numpy as np

import twitter_credentials as twi_cre

# authorization of consumer key and consumer secret
auth = tweepy.OAuthHandler(twi_cre.consumer_key, twi_cre.consumer_secret)


# set access to user's access key and access secret
auth.set_access_token(twi_cre.access_token, twi_cre.access_token_secret)

# calling the api
api = tweepy.API(auth)

from tweepy.streaming import StreamListener
import json
import time
import sys

print("Vérifier que le dossier où s'enregistront les streams est bien le bon")


class SListener(StreamListener):
    def __init__(self, api=None, fprefix="streamer", path=""):
        self.api = api or tweepy.API()
        self.counter = 0
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
        print("Stream restarted")

    def on_timeout(self):
        print(sys.stderr, "Timeout...")
        return True  # Don't kill the stream
        print("Stream restarted")


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
