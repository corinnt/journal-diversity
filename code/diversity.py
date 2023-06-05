import sys
import argparse
import requests
import pandas as pd
import geopandas as gpd

import parseDetails
from map import map_points
from util import info, valid_title

VERBOSE = False

class Data():
    def __init__(self):
        self.titles = []
        self.authors = []
        self.concepts = []
        self.years = []

        self.latitudes = []
        self.longitudes = []

        self.countries = {}
        self.institutions = {}
        self.institution_ids = set()

def main(args):
    data = Data()
    if args.journal_name:
        args.id = get_journal_id(args.journal_name)
    iterate_search(args, data)
    display_data(data, write_csv=args.csv, write_maps=args.maps)    

def parseArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("email", help="the reply-to email for OpenAlex API calls") # required=True,
    parser.add_argument("-v", "--verbose", action="store_true", help="include to print progress messages")
    parser.add_argument("-n", "--journal_name", dest="journal_name", type=str, default=None, help="name of journal or source to search for")
    parser.add_argument("-i", "--journal_id", dest="id", type=str, default="S21591069", help="OpenAlex id of journal to analyze - defaults to Gesta if unspecified") 
    parser.add_argument("-c", "--write_csv", dest="csv", action="store_true", help="include to write csv of data") 
    parser.add_argument("-m", "--write_maps", dest="maps", action="store_true", help="include to plot locations of affiliated institutions") 
    parser.add_argument("--start_year", dest="start_year", type=int, default=None, help="filter publication dates by this earliest year (inclusive)")
    parser.add_argument("--end_year", dest="end_year", type=int, default=None, help="filter publication dates by this latest year (inclusive)")
    args = parser.parse_args()
    if args.verbose: 
        global VERBOSE 
        VERBOSE = True
    return args

def get_journal_id(args):
    url = "https://api.openalex.org/sources?search=" + args.journal_name + '&mailto=' + args.email
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        results = response.json()
        if 'id' in results:
            info("got id of " + args.journal_name) # POSSBUG: multiple journals of same name
            return results['id']
    except requests.exceptions.RequestException as e:
        print("Error occurred:", e)
    except ValueError as e:
        print("Error decoding JSON:", e)

def iterate_search(args, data):
    """
    :param source_id: string - OpenAlex ID of the source to analyze
    :param data: empty Data object
    """
    # only get name and authors for after 1999
    fields = 'display_name,authorships,concepts,publication_year'
    search_filters = 'locations.source.id:' + args.id
    if args.start_year:
        search_filters += ',publication_year:>' + str(args.start_year - 1)
    if args.end_year: 
        search_filters += ',publication_year:<' + str(args.end_year + 1)

    works_query_with_page = 'https://api.openalex.org/works?select=' + fields + '&filter=' + search_filters + '&page={}&mailto=' + args.email
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
                parseDetails.parse_work(work, data)
            
        page += 1
            
        # end loop when either there are no more results on the requested page 
        # or the next request would exceed 10,000 results
        page_size = page_with_results['meta']['per_page']
        has_more_pages = len(results) == page_size
        fewer_than_10k_results = page_size * page <= 10000
        info("iterating through pages: on page " + str(page))

def display_data(data, write_csv=False, write_maps=False):
    """
        :param data: filled Data object 
        :param write_csv: 
    """
    #print(data.institutions)
    dict = {'author' : data.authors, 'title' : data.titles, 'year' : data.years, 'keywords' : data.concepts}
    df = pd.DataFrame(dict)
    print(df.head())
    
    if write_csv: 
        info("writing csv...")
        df.to_csv("../data/data.csv")

    if write_maps:
        info("mapping points...")
        map_dict = {'latitude' : data.latitudes, 'longitude' : data.longitudes}
        map_df = pd.DataFrame(map_dict)
        global_map = gpd.read_file('../shapefiles/world-map/WB_Land_10m.shp')
        map_points(map_df, global_map, 'world')
        us_map = gpd.read_file('../shapefiles/us-map/tl_2012_us_state.shp')
        map_points(map_df, us_map, 'US')

if __name__ == "__main__":
    args = parseArguments()
    main(args)
 