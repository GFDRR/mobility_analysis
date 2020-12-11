### import key libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import glob, os
from datetime import datetime as dt
from datetime import timedelta
from datetime import timezone
import pytz

import geopandas as gpd
import contextily as ctx
import pyproj

def visualize_simpleplot(df):
    gdf = gpd.GeoDataFrame(df, 
                           geometry=gpd.points_from_xy(df.lon, df.lat),
                           crs= {"init": "epsg:4326"}).to_crs(epsg=3857)
    fig,ax = plt.subplots(figsize=(15,10))
    xmin, ymin, xmax, ymax = gdf.total_bounds
    basemap, extent = ctx.bounds2img(xmin, ymin, xmax, ymax, 
                                     source=ctx.providers.CartoDB.Voyager)
    gdf.plot(ax=ax, zorder=2)
    ax.imshow(basemap, extent=extent, zorder=1)
    plt.show()

def visualize_boundarymap(boundary):
    fig,ax = plt.subplots(figsize=(15,10))
    x1, y1 = (boundary[0], boundary[1])
    x2, y2 = (boundary[2], boundary[3])
    basemap, extent = ctx.bounds2img(x1, y1, x2, y2, ll=True,
                                     source=ctx.providers.CartoDB.Voyager)
    ax.imshow(basemap, extent=extent)
    plt.show()