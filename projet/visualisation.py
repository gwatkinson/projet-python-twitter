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


def create_gdf():
    states = us.STATES
    urls = [state.shapefile_urls("state") for state in states]
    gdf = pd.concat([gpd.read_file(url) for url in urls]).pipe(gpd.GeoDataFrame)
    return gdf[["STUSPS10", "NAME10", "geometry"]]


def save_hist(df, df_state, label="kmlabel"):
    def _add_image(row):
        state = row["NAME10"]
        if any(df["state"] == state):
            df2 = df[df["state"] == state].groupby(label).describe()
            m = df2["user-id"]["count"]
            fig = m.plot(
                kind="bar", title=f"Histogramme de {state}", x=label, y="Count",
            ).get_figure()
            file = f"image/hist_{label}/hist_{label}_{state}.jpg"
            fig.savefig(file)
            return file
        return "No data"

    df_state[f"hist_{label}"] = df_state.apply(_add_image, axis=1)

    return df_state


def add_max(df, df_state, label="kmlabel"):
    def _add_max(row):
        state = row["NAME10"]
        if any(df["state"] == state):
            df2 = df[df["state"] == state].groupby(label).describe()
            m = df2["user-id"]["count"]
            return m.idxmax()
        return np.nan

    df_state[f"cluster_max_{label}"] = df_state.apply(_add_max, axis=1)

    return df_state


def add_stats_sentiment(df, df_state):
    df2 = df.groupby("state").describe()["full_text-sentiment-compound"][
        ["count", "mean", "std"]
    ]
    df_state = df_state.merge(df2, how="left", left_on=["NAME10"], right_on=["state"])

    return df_state


def plot_hist(df_state, label="kmlabel"):
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
                    src="@hist_label" alt="No image" width="300" height="300"
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
        title=f"Histogramme de '{label}'",
        plot_height=600,
        plot_width=950,
        tools=[hover, "pan,wheel_zoom,box_zoom,reset"],
        toolbar_location="right",
        x_range=(-130, -64),
        y_range=(22, 50),
    )
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None

    n = df_state[f"cluster_max_{label}"].nunique()
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
        fill_color={"field": f"cluster_max_{label}", "transform": color_mapper},
        line_color="black",
        line_width=1,
        fill_alpha=1,
    )

    # Save map in html
    output_file(f"image/maps/map_{label}.html", mode="inline")

    # Display figure inline in Jupyter Notebook.
    output_notebook()

    # Save figure.
    # save(p)
    # Display figure.
    show(p)
