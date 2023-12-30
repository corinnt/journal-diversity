import numpy as np
import util

def parse_work_geodata(institutions_and_authors, i):
    """ Given list of institution IDs and author IDs, 
        returns a list of latitudes and longitudes for those authors
        Args:
            institution_and_authors: list[tuple(institution_id, author_id)] 
            i : int - batch index. NOTE: Target function for multiprocessing
    """ 
    print("institution_author_batch: " + str(institutions_and_authors[0]))
    institution_batch, author_batch = institutions_and_authors[0]
    #latitude, longitude = np.nan, np.nan
    for institution in institution_batch:
        latitude, longitude = institution_id_geodata(institution)
        if latitude != np.nan: 
            print ("institution geodata.\tlatitude: " + str(latitude) + "\tlongitude: " + str(longitude) + "\ti: " + str(i)+ "\n")
            return latitude, longitude, i
    for author in author_batch:
        latitude, longitude = author_id_geodata(author)
        if latitude != np.nan: 
            print ("alternate geodata.\tlatitude: " + str(latitude) + "\tlongitude: " + str(longitude) + "\ti: " + str(i)+ "\n")
            return latitude, longitude, i
    print ("no geodata.\tlatitude: " + str(latitude) + "\tlongitude: " + str(longitude) + "\ti: " + str(i) + "\n")
    return latitude, longitude, i
        # none of the institutions or authors had geodata
        
def institution_id_geodata(id):
    """ Given an Institution ID, adds 
        Args:
            id: - string ID of Institution to check for geodata
        Returns
            (float, float) - latitude and longitude of 
    """
    lat, long = np.nan, np.nan
    if not id: 
        util.info("Blank ID passed to parse_geodata")
        return lat, long

    url =  "https://api.openalex.org/institutions/" + id
    institution = util.api_request(url)
    if not institution: return lat, long
    display_name = institution['display_name']
    if 'latitude' in institution['geo']:
        lat = institution['geo']['latitude']
        long = institution['geo']['longitude']
        return lat, long
    else:
        util.info("Geo information unavailable for " + display_name)
        return lat, long
        
def author_id_geodata(id):
    """
        :param authorship: string id of Author to check for most recent institution's geodata
        :return bool: returns True if successfully found institution/location info to Data
    """
    lat, long = np.nan, np.nan
    if not id: return lat, long
    url =  "https://api.openalex.org/authors/" + id
    author = util.api_request(url)
    if not author: return lat, long #, 'NA'

    if author['last_known_institution']:
        institution_id = author['last_known_institution']['id']
        lat, long = institution_id_geodata(institution_id) # , name
        #util.info("Adding last known institution " + name + ".")
        return lat, long #, "last known: " + name
    else:
        #util.info("Last known institution unavailable.")
        return lat, long #, 'NA'