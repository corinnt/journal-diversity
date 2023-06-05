import pandas as pd
import matplotlib.pyplot as plt
import descartes
import geopandas as gpd
from shapely.geometry import Point, Polygon

def map_points(df, map, name): 
    """
        :param df: DataFrame with longitude and latitude data for points
        :param map: GeoPandas
    """ 
    geometry = [Point(xy) for xy in zip(df['longitude'], df['latitude'])]
    fig, ax = plt.subplots(figsize=(15,15))
   
    crs = {'init':'epsg:4326'}
    geo_df = gpd.GeoDataFrame(df, crs=crs, geometry=geometry) #specify the geometry list we created
    map.plot(ax=ax, color='grey', alpha=0.4)
    geo_df.plot(ax=ax, 
                aspect=1,
                markersize=10, 
                color='blue', 
                marker='o')
    plt.savefig("../data/" + name + ".jpg")
    geo_df.head()