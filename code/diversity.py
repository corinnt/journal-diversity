import sys
import argparse
import requests
import pandas as pd
import numpy as np

from tqdm import tqdm

import parseDetails
from map import map_points
from util import valid_title, unpickle_data, pickle_data

VERBOSE = False
def info(text):
    global VERBOSE
    if VERBOSE:
        print(text)

class Data():
    def __init__(self, args):
        self.titles = []
        self.authors = []
        self.abstracts = []
        self.concepts = []
        self.years = []
        self.institution_names = []

        self.latitudes = []
        self.longitudes = []

        self.config = args
        self.id = None
        #self.num_works = 0

def parseArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("email", help="the reply-to email for OpenAlex API calls") # required=True,
    parser.add_argument("-v", "--verbose", action="store_true", help="include to print progress messages")
    parser.add_argument("-n", "--journal_name", dest="journal_name", type=str, default=None, help="name of journal or source to search for")
    parser.add_argument("-c", "--write_csv", dest="csv", action="store_true", help="include to write csv of data") 
    parser.add_argument("-a", "--write_abstracts", action="store_true", help="include to write abstracts of all works to csv") 
    parser.add_argument("-m", "--write_maps", dest="maps", action="store_true", help="include to plot locations of affiliated institutions") 
    parser.add_argument("-r", "--restore_saved", action="store_true", help="include to restore saved data") 
    parser.add_argument("--start_year", dest="start_year", type=int, default=None, help="filter publication dates by this earliest year (inclusive)")
    parser.add_argument("--end_year", dest="end_year", type=int, default=None, help="filter publication dates by this latest year (inclusive)")
    args = parser.parse_args()
    if args.verbose: 
        global VERBOSE 
        VERBOSE = True
    return args

def main(args):
    data = Data(args)
    if args.journal_name:
        data.id = get_journal_id(args.journal_name)
    else:
        data.id = 'S21591069' # Default Gesta
        data.num_works = 1091

    if args.restore_saved:
        data = unpickle_data('../data/pickled_data')
    else:
        iterate_search(args, data)
        pickle_data(data)

    display_data(data)    

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
    fields = 'display_name,authorships,concepts,publication_year,abstract_inverted_index'
    search_filters = 'locations.source.id:' + data.id
    if args.start_year:
        search_filters += ',publication_year:>' + str(args.start_year - 1)
    if args.end_year: 
        search_filters += ',publication_year:<' + str(args.end_year + 1)

    works_query_with_page = 'https://api.openalex.org/works?select=' + fields + '&filter=' + search_filters + '&page={}&mailto=' + args.email
    page = 1
    has_more_pages = True
    fewer_than_10k_results = True

    #for page in tqdm(range(int(data.num_works/25))):
    while has_more_pages and fewer_than_10k_results:
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
        if page % 5 == 0:
            info("iterating through pages: on page " + str(page))

def display_data(data):
    """
        :param data: filled Data object with config fields write_csv, maps, 
    """
    dict = {'author' : data.authors, 
            'title' : data.titles, 
            'year' : data.years,
            'institution' : data.institution_names, 
            #'last known institution' : data.last_known_institutions,
            'latitude' : data.latitudes, 
            'longitude' : data.longitudes}

    if data.config.write_abstracts: 
        dict['abstract'] = data.abstracts
    df = pd.DataFrame(dict)
    info(df.head())
    
    if data.config.csv: 
        info("writing csv...")
        df.to_csv("../data/data.csv")

    if data.config.maps:
        info("mapping points...")
        map_dict = {'latitude' : data.latitudes, 'longitude' : data.longitudes} 
        map_df = pd.DataFrame(map_dict)
        df = map_df.groupby(['longitude', 'latitude']).size().reset_index(name='counts')
        map_points(df, 'world')
        info("maps created!")

if __name__ == "__main__":
    args = parseArguments()
    main(args)
 