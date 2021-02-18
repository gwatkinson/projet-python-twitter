# Projet python twitter

[![Python application](https://github.com/gwatkinson/projet-python-twitter/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/gwatkinson/projet-python-twitter/actions/workflows/python-app.yml)

Ceci est notre projet d'informatique de 2<sup>ème</sup> année de l'ENSAE pour le cours *Python pour un data scientist* où nous avons choisis d'utiliser l'**API de Twitter** et du **sentimental analysis**.

**Problématique** : $\underline{​​\text{​​ En quoi Twitter reflète-t-il la polarisation aux États-Unis, autour des élections présidentielles Américaines ?}​​}​​$

## Installation

Récupération du projet sur GitHub avec :

        git clone https://github.com/gwatkinson/projet-python-twitter.git
        cd projet-python-twitter

Upgrade pip :

        python3 -m pip install --upgrade pip

Créer un environnement virtuel :

        pip install virtualenv
        virtualenv .venv
        source .venv/bin/activate
        # .venv\Scripts\activate # sur Windows

Pour utiliser directement le `setup.py` :

        pip install .

Sinon, installer directement des packages nécessaire :

        pip install -r requirements.txt

Puis, il faut créer le fichier `projet/_credentials.py`, qui contient les clés de l'API de Twitter.

Dans le format suivant :

```python
    credentials = {
        "consumer_key": "XXXXXXX",
        "consumer_secret": "XXXXXXX",
        "access_token": "XXXXXXX",
        "access_token_secret": "XXXXXXX",
}
```

Finalement, il faut ajouter les données dans le dossier `data/json/`.

## Modules

* <a href="https://gwatkinson.github.io/projet-python-twitter/projet/streaming.html" target="_blank">streaming</a>
* <a href="https://gwatkinson.github.io/projet-python-twitter/projet/processing.html" target="_blank">processing</a>
* <a href="https://gwatkinson.github.io/projet-python-twitter/projet/modelisation.html" target="_blank">modelisation</a>
* <a href="https://gwatkinson.github.io/projet-python-twitter/projet/visualisation.html" target="_blank">visualisation</a>

## Documentation

<a href="https://gwatkinson.github.io/projet-python-twitter/" target="_blank">https://gwatkinson.github.io/projet-python-twitter/</a>

## Auteurs

* Gabriel Watkinson
* Mathias Vigouroux
* Wilfried Yapi
