import pandas as pd
import matplotlib.pyplot as plt
import descartes
import geopandas as gpd
from shapely.geometry import Point, Polygon



def map_points(points, csv_path): 
    """
        :param points: list of tuples of latitudes and longitudes
        :param csv_path: path to csv with data to map
    """ 
    map = gpd.read_file('../world-map-shapefile/WB_Land_10m.shp')
    geometry = [Point(xy) for xy in points]
    fig, ax = plt.subplots(figsize=(15,15))
    map.plot(ax=ax)
    plt.savefig('world.jpg')

    """
       df = pd.read_csv(csv_path)
    crs = {'init':'epsg:4326'}
    geo_df = gpd.GeoDataFrame(df, #specify our data
                          crs=crs #specify our coordinate reference system
                          geometry=geometry) #specify the geometry list we created
    
    """
 
    #geo_df.head()