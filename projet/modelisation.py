"""Modélisattion sur la df"""

# Import les modules utilisés
import pandas as pd
import numpy as np
import glob
import nltk
import sklearn
import matplotlib.pyplot as plt
from kneed import KneeLocator
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

# Import les utils du projet
import projet.projet_utils as utils


# Fonctions pour le K-means
def get_numeric(df):
    return list(df.select_dtypes(include=[np.number, bool]))


def standardize(df, vars):
    """
    Normalise les données.

    Args:
        df (pandas.dataframe): Une df avec les données.
        vars (list): Liste des noms des variables à normaliser.

    Returns:
        pandas.dataframe: Une df normalisée.
    """
    new_df = df[vars].astype(float)
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(new_df)

    return pd.DataFrame(scaled_features, columns=new_df.columns)


def add_group(df, max_cluster=10):
    kmeans_kwargs = {
        "init": "random",
        "n_init": 10,
        "max_iter": 300,
        "random_state": 42,
    }

    # A list holds the SSE values for each k
    sse = []
    for k in range(1, max_cluster + 1):
        kmeans = KMeans(n_clusters=k, **kmeans_kwargs)
        kmeans.fit(df)
        sse.append(kmeans.inertia_)

    kl = KneeLocator(
        range(1, max_cluster + 1), sse, curve="convex", direction="decreasing"
    )

    print(kl.elbow)

    kmeans = KMeans(n_clusters=kl.elbow, **kmeans_kwargs)

    return kmeans.fit(df), sse
