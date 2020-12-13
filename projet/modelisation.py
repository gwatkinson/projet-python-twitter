"""Modélisattion sur les données"""

# Import les modules utilisés
import pandas as pd
import numpy as np
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
def get_numeric(df, drop_vars=["user-id"]):
    return list(df.drop(drop_vars, axis=1).select_dtypes(include=[np.number, bool]))


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


def KM(
    df,
    n_cluster=None,  # Prend la valeur optimal
    label_var="kmlabel",
    vars=None,
    drop_vars=["user-id"],
    n_init=10,
    max_iter=300,
    max_cluster=10,
    random_state=40,
    plot=False,
):

    if vars is None:
        vars = get_numeric(df, drop_vars)
    df2 = standardize(df, vars=vars)

    kmeans_kwargs = {
        "init": "random",
        "n_init": n_init,
        "max_iter": max_iter,
        "random_state": random_state,
    }

    # A list holds the SSE values for each k
    if n_cluster is None:
        sse = []
        for k in range(1, max_cluster + 1):
            kmeans = KMeans(n_clusters=k, **kmeans_kwargs)
            kmeans.fit(df2)
            sse.append(kmeans.inertia_)

        kl = KneeLocator(
            range(1, max_cluster + 1), sse, curve="convex", direction="decreasing"
        )

        n_cluster = kl.elbow

        if plot:
            plt.style.use("fivethirtyeight")
            plt.plot(range(1, max_cluster + 1), sse, label="SSE")
            plt.vlines(
                n_cluster,
                min(sse),
                max(sse),
                colors="r",
                linestyles="dotted",
                label="Nombre de clusters",
            )
            plt.xticks(range(1, max_cluster + 1))
            plt.xlabel("Number of Clusters")
            plt.ylabel("SSE")
            plt.legend()
            plt.show()

    kmeans = KMeans(n_clusters=n_cluster, **kmeans_kwargs)

    km = kmeans.fit(df2)

    df[label_var] = km.labels_

    return df
