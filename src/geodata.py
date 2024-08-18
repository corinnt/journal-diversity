import numpy as np
import pygmt as pgm
import util
from multiRequests import api_get


def parse_work_geodata(institutions_and_authors, i):
    """ 
        NOTE: Target function for multiprocessing
        Given list of institution IDs and author IDs, 
        returns a list of latitudes and longitudes for those authors
        Args:
            institution_and_authors: list[tuple(institution_id, author_id)] 
            i : int - batch index.
        Returns: 
            latitude, longitude, i for the institution if found, else author's last known insitution
    """ 
    institution_batch, author_batch = institutions_and_authors[0]
    latitude, longitude = np.nan, np.nan
    for institution in institution_batch:
        latitude, longitude = institution_id_geodata(institution)
        if latitude != np.nan: 
            return latitude, longitude, i
    for author in author_batch:
        latitude, longitude = author_id_geodata(author)
        if latitude != np.nan: 
            return latitude, longitude, i
    return latitude, longitude, i         # none of the institutions or authors had geodata
        
def institution_id_geodata(id):
    """ Given an Institution ID, returns latitudes and longitudes of institution
        Args:
            id: string ID of Institution to check for geodata
        Returns
            (float, float) - latitude and longitude of institution
    """
    lat, long = np.nan, np.nan
    if not id: return lat, long

    url =  "https://api.openalex.org/institutions/" + id
    institution = api_get(url)
    if not institution: return lat, long

    if 'latitude' in institution['geo']:
        lat = institution['geo']['latitude']
        long = institution['geo']['longitude']
    return lat, long
        
def author_id_geodata(id):
    """ Given an author ID, returns the latitude and longitude of their last known institution
        Args:
            id: string ID of Author to check for geodata (most recent institution)
        Returns: 
            (float, float) - latitude and longitude of author's most recent institution
    """
    lat, long = np.nan, np.nan
    if not id: return lat, long

    url =  "https://api.openalex.org/authors/" + id
    author = api_get(url)
    if not author: return lat, long
    if author['last_known_institutions']:
        if len(author['last_known_institutions']) > 0: 
            institution_id = author['last_known_institutions'][0]['id']
            lat, long = institution_id_geodata(institution_id)
    return lat, long

def map_points(df, path): 
    """ Given a df with latitude, longitude, and counts, generating a map plotting the locations 
        to file specified by config
    """
    region = [-180, 180,
                -60, 80,]
    fig = pgm.Figure()
    fig.basemap(region=region, projection="M8i", frame=True)
    fig.coast(land="black", water="skyblue")
    fig.plot(x=df.longitude, y=df.latitude, style="c0.3c", fill="black", pen="black")
 
    fig = pgm.Figure()
    fig.basemap(region=region, projection="M8i", frame=True)
    fig.coast(land="lightblue", water="white")
    #fig.coast(land="sage?", water="white")
    fig.plot(
        x=df.longitude,
        y=df.latitude,
        size=0.08 + 0.04*(np.log2(df.counts)),
        style="cc",
        fill='black',
        #fill="darkblue",
        #fill="gray40",
        transparency=60
    )
    fig.savefig(path)