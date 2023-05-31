from operator import truediv
from readline import insert_text
import requests
import pandas as pd
import geopandas as gpd

from mailto import email # just a function that returns your email address
from map import map_points

class Data():
    def __init__(self):
        self.titles = []
        self.authors = []
        self.years = []

        self.latitudes = []
        self.longitudes = []

        self.countries = {}
        self.institutions = {}
        self.institution_ids = set()


def main(source_id):
    issn_l = "0016-920X"
    source_query = "https://api.openalex.org/sources/" + source_id
    data = Data()
    iterate_search(source_id, data)
    display_data(data, write_maps=True)    
    # TODO: make protocol for what fields to query?
    # ie get institution ID, else get institution name and country, else get author name and country and year?

def increment(key, dict):
    if key in dict:
        dict[key] += 1
    else:
        dict[key] = 1

def valid_title(title):
    """ 
        Given a title, returns true if the title is not 
            :param title: prospective title 
    """
    status = title and\
            title != "Front Matter" and\
            title != "Back Matter" and\
            title != "Front Cover" and\
            title != "Back Cover"
    return status

def parse_work(work, data):
    """
        :param work:
        :param data: partially full Data object
    """
    title = work['display_name']
    if not title: title = 'NA'
    data.titles.append(title)

    year = str(work['publication_year'])
    if not year: 
        year = 'NA'
    data.years.append(year)

    authorship_list = work['authorships']
    if authorship_list:
        parse_authorship(authorship_list, data)
    else:
        data.authors.append('NA')

def parse_authorship(authorships, data):
    """
        :param authorships: list of authorship objects from the OpenAlex API
        :param data: partially full Data object
    """
    author_string = ""
    for authorship in authorships:
        author_string += authorship['author']['display_name'] + "\n"
        for institution in authorship['institutions']:
            code = institution['country_code']
            id = institution['id']
            if id: parse_geodata(id, data)
            increment(code, data.countries)
            increment(id, data.institutions)
            data.institution_ids.add(id)
    data.authors.append(author_string)

def parse_geodata(id, data):
    """
        :param id: - string ID of Institution to check for geodata
        :param data: - partially full Data object
    """
    url =  "https://api.openalex.org/institutions/" + id
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        results = response.json()
        if 'latitude' in results['geo']:
            print("got latitude")
            lat = results['geo']['latitude']
            long = results['geo']['longitude']
            data.latitudes.append(lat)
            data.longitudes.append(long)
    except requests.exceptions.RequestException as e:
        print("Error occurred:", e)
    except ValueError as e:
        print("Error decoding JSON:", e)

def iterate_search(source_id, data):
    """
    :param source_id: string - OpenAlex ID of the source to analyze
    :param data: empty Data object
    """
    # only get name and authors for after 1999
    works_query_with_page = 'https://api.openalex.org/works?select=display_name,authorships,concepts,publication_year&filter=locations.source.id:' + source_id + '&page={}&mailto=' + email()
    #publication_year:>1999
    page = 1
    has_more_pages = True
    fewer_than_10k_results = True

    while has_more_pages and fewer_than_10k_results:
    #while page == 1:
        # set page value and request page from OpenAlex
        url = works_query_with_page.format(page)
        page_with_results = requests.get(url).json()
            
        # loop through page of results
        results = page_with_results['results']
        for i, work in enumerate(results):
            title = work['display_name']
            if valid_title(title):
                parse_work(work, data)
            
        page += 1
            
        # end loop when either there are no more results on the requested page 
        # or the next request would exceed 10,000 results
        page_size = page_with_results['meta']['per_page']
        has_more_pages = len(results) == page_size
        fewer_than_10k_results = page_size * page <= 10000

def display_data(data, write_csv=False, write_maps=False):
    """
        :param data: filled Data object 
        :param write_csv: 
    """
    #print(data.institutions)
    dict = {'author' : data.authors, 'title' : data.titles, 'year' : data.years}
    df = pd.DataFrame(dict)
    print(df.head())
    
    if write_csv: df.to_csv("../data/data.csv")

    if write_maps:
        map_dict = {'latitude' : data.latitudes, 'longitude' : data.longitudes}
        map_df = pd.DataFrame(map_dict)
        global_map = gpd.read_file('../shapefiles/world-map/WB_Land_10m.shp')
        map_points(map_df, global_map, 'world')
        us_map = gpd.read_file('../shapefiles/us-map/tl_2012_us_state.shp')
        map_points(map_df, us_map, 'US')

if __name__ == "__main__":
    gesta_id = "S21591069"
    main(gesta_id)
 