"""Visualisation des données"""

from bokeh.io import output_notebook, show, output_file, save
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar
from bokeh.palettes import brewer, d3
from bokeh.io import curdoc, output_notebook
from bokeh.models import Slider, HoverTool
from bokeh.layouts import widgetbox, row, column
import json
import numpy as np
import pandas as pd
import geopandas as gpd
import us
import matplotlib.pyplot as plt


def create_gdf(vars=["STUSPS10", "NAME10", "geometry"]):
    """
    Créée une geodataframe geopandas avec les États américains.

    Args:
        vars (list, optional): Liste des variables à garder.    
            Par défaut : `["STUSPS10", "NAME10", "geometry"]`.

    Returns:
        geopandas.geodataframe: Une gdf de 50 lignes contenant la forme des États américains.
    """
    states = us.STATES
    urls = [state.shapefile_urls("state") for state in states]
    gdf = pd.concat([gpd.read_file(url) for url in urls]).pipe(gpd.GeoDataFrame)
    return gdf[vars]


def add_max(
    df,
    df_state,
    label="kmlabel",
    var_state_df="state",
    var_state_gdf="NAME10",
    new_var="cluster_max",
):
    """
    Ajoute le cluster majoritaire dans chaque État.

    Args:
        df (pandas.dataframe): La dataframe pandas avec les labels.

        df_state (geopandas.geodataframe): La gdf des États.

        label (str, optional): Le label à utiliser.    
            Par défaut : `"kmlabel"`.

        var_state_df (str, optional): Nom de la variable du nom des États dans la df.    
            Par défaut : `"state"`.

        var_state_gdf (str, optional): Nom de la variable du nom des États dans la gdf.    
            Par défaut : `"NAME10"`.

        new_var (str, optional): Nom de la nouvelle variable.    
            Le suffixe _{label} est ajouté.    
            Par défaut : `"cluster_max"`.

    Returns:
        geopandas.geodataframe: Modifie et renvoie la gdf des États avec le cluster majoritaire.
    """

    def _add_max(row):
        state = row[var_state_gdf]
        if any(df[var_state_df] == state):
            df2 = df[df[var_state_df] == state].groupby(label).describe()
            m = df2["user-id"]["count"]
            return m.idxmax()
        return np.nan

    df_state[f"{new_var}_{label}"] = df_state.apply(_add_max, axis=1)

    return df_state


def add_stats_sentiment(
    df,
    df_state,
    sent_var="full_text-sentiment-compound",
    var_state_df="state",
    var_state_gdf="NAME10",
):
    """
    Ajoute des stats descriptive sur le compound du texte (count, mean, std).

    Args:
        df (pandas.dataframe): La dataframe pandas avec les labels.

        df_state (geopandas.geodataframe): La gdf des États.

        var_state_df (str, optional): Nom de la variable du nom des États dans la df.    
            Par défaut : `"state"`.

        var_state_gdf (str, optional): Nom de la variable du nom des États dans la gdf.    
            Par défaut : `"NAME10"`.

    Returns:
        geopandas.geodataframe: Modifie et renvoie la gdf des États avec les stats descriptive sur le compound du texte.
    """
    df2 = df.groupby(var_state_df).describe()[sent_var][["count", "mean", "std"]]
    df_state = df_state.merge(
        df2, how="left", left_on=[var_state_gdf], right_on=[var_state_df]
    )

    return df_state


def save_hist(
    df,
    df_state,
    label="kmlabel",
    var_state_df="state",
    var_state_gdf="NAME10",
    path="image/hist",
    new_var="hist",
):
    """
    Créée les images des histogrammes par États puis ajoute une colonne avec les chemins vers les images.

    Args:
        df (pandas.dataframe): La dataframe pandas avec les labels.

        df_state (geopandas.geodataframe): La gdf des États.

        label (str, optional): Le label à utiliser.    
            Par défaut : `"kmlabel"`.

        var_state_df (str, optional): Nom de la variable du nom des États dans la df.    
            Par défaut : `"state"`.

        var_state_gdf (str, optional): Nom de la variable du nom des États dans la gdf.    
            Par défaut : `"NAME10"`.

        path (str, optional): Chemin où mettre les images.    
            Le suffixe _{label} est ajouté.    
            Par défaut : `"image/hist"`.

        new_var (str, optional): Nom de la nouvelle variable.    
            Le suffixe _{label} est ajouté.    
            Par défaut : `"hist"`.

    Returns:
        geopandas.geodataframe: Modifie et renvoie la gdf des États avec une colonne pour les histogrammes.
    """

    def _add_image(row):
        state = row[var_state_gdf]
        if any(df[var_state_df] == state):
            df2 = df[df[var_state_df] == state].groupby(label).describe()
            m = df2["user-id"]["count"]
            plt.figure(figsize=(10,10))
            fig = m.plot(
                kind="bar", title=f"Histogramme de {state}", x=label, y="Count",
            ).get_figure()
            file = f"{path}_{label}/hist_{label}_{state}.jpg"
            fig.savefig(file)
            plt.close()
            return file
        return "No data"

    df_state[f"{new_var}_{label}"] = df_state.apply(_add_image, axis=1)

    return df_state


def plot_hist(
    df_state, label="kmlabel", path="", new_var="map", fill_var="cluster_max",
):
    """
    Créée et affiche une carte interactive avec Bokeh.

    Args:
        df_state (geopandas.geodataframe): La gdf des États
            qui contient les images des histogrammes.

        label (str, optional): Le label à utiliser.    
            Par défaut : `"kmlabel"`.

        path (str, optional): Chemin où mettre les images.    
            Par défaut : `""`.

        new_var (str, optional): Nom de la nouvelle variable.    
            Le suffixe _{label} est ajouté.    
            Par défaut : `"map"`.

        fill_var (str, optional): Nom de la variable des couleurs de la carte.    
            Le suffixe _{label} est ajouté.    
            Par défaut : `"cluster_max"`.
    """
    # Fill nan
    df_state.fillna("No data", inplace=True)

    # Read data to json.
    df_state_json = json.loads(df_state.to_json())

    # Convert to String like object.
    json_data = json.dumps(df_state_json)

    # Input GeoJSON source that contains features for plotting.
    geosource = GeoJSONDataSource(geojson=json_data)

    tooltips_dict = {
        "kmlabel": """
        <div>
            <div>
                <img
                    src="@hist_kmlabel" alt="No image" width="300" height="300"
                    style="float: left; margin: 0px 0px 0px 0px;"
                    border="0"
                ></img>
            </div>
        </div>
    """,
        "label": """
        <div>
            <div>
                <img
                    src="@hist_label" alt="No image" width="500" height="500"
                    style="float: left; margin: 0px 0px 0px 0px;"
                    border="0"
                ></img>
            </div>
        </div>
    """,
    }

    # Add hover tool
    hover = HoverTool(tooltips=tooltips_dict[label])

    # Create figure object.
    p = figure(
        plot_height=600,
        plot_width=950,
        tools=[hover, "pan,wheel_zoom,box_zoom,reset"],
        toolbar_location="right",
        x_range=(-130, -64),
        y_range=(22, 50),
    )
    p.title.text = f"Histogramme de '{label}'"
    p.title.align = "center"
    p.title.text_font_size = "25px"
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None

    n = df_state[f"{fill_var}_{label}"].nunique()
    if n > 10:
        pal = brewer["YlGnBu"]
    else:
        pal = brewer["Set3"]
    palette = pal[n]
    color_mapper = LinearColorMapper(
        palette=palette, low=0, high=n, nan_color="#d9d9d9"
    )
    # Add patch renderer to figure.
    p.patches(
        "xs",
        "ys",
        source=geosource,
        fill_color={"field": f"{fill_var}_{label}", "transform": color_mapper},
        line_color="black",
        line_width=1,
        fill_alpha=1,
    )

    # Save map in html
    output_file(f"{path}{new_var}_{label}.html", mode="inline")

    # Display figure inline in Jupyter Notebook.
    output_notebook()

    # Save figure.
    # save(p)
    # Display figure.
    show(p)
