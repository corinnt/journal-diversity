import sys
import argparse
import requests
import pandas as pd
import numpy as np

from tqdm import tqdm

import parseDetails
import util
import gender

from map import map_points

class Data():
    def __init__(self, args):
        self.titles = []
        self.authors = []
        self.abstracts = []
        self.concepts = []
        self.years = []
        self.institution_names = []
        self.gender_strings = []
        self.author_ids = []
        self.gender_data = None

        self.latitudes = []
        self.longitudes = []

        self.config = args
        self.id = None
        self.num_works = 0

def parseArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("email", help="the reply-to email for OpenAlex API calls") # required=True,
    parser.add_argument("-v", "--verbose", action="store_true", help="include to print progress messages")

    parser.add_argument("-n", "--journal_name", dest="journal_name", 
        type=str, default=None, help="name of journal or source to search for")

    parser.add_argument("-c", "--write_csv", dest="csv", 
        action="store_true", help="include to write csv of data") 

    parser.add_argument("-a", "--write_abstracts", dest="abstracts", 
        action="store_true", help="include to write abstracts of all works to csv") 

    parser.add_argument("-g", "--predict_gender", dest="gender", 
        action="store_true", help="include to predict genders of all authors and write to csv") 

    parser.add_argument("-m", "--write_maps", dest="maps", 
        action="store_true", help="include to plot locations of affiliated institutions") 

    parser.add_argument("-r", "--restore_saved", action="store_true", help="include to restore saved data") 
    parser.add_argument("--start_year", dest="start_year", type=int, default=None, help="filter publication dates by this earliest year (inclusive)")
    parser.add_argument("--end_year", dest="end_year", type=int, default=None, help="filter publication dates by this latest year (inclusive)")

    args = parser.parse_args()
    if args.verbose: 
        util.VERBOSE = True
    return args

def main(args):
    
    data = Data(args)

    if args.journal_name:
        data.id, data.num_works = get_journal_id(args.journal_name)
    else:
        data.id = 'S21591069' # Default Gesta
        data.num_works = 1091

    if args.restore_saved:
        data = util.unpickle_data('../data/pickled_data')
        display_data(data)    
    else:
        iterate_search(args, data)
        display_data(data)    
        util.pickle_data(data)


    

def get_journal_id(args):
    """ Returns the OpenAlex Work ID of the top result matching the input journal name
    :param args: parsed user argument object
    :returns str, int: ID of journal, count of Works in source
    """
    FAIL = "", 0
    
    url = "https://api.openalex.org/sources?search=" + args.journal_name + '&mailto=' + args.email
    results = util.api_request(url)
    if not results: return FAIL

    if len(results['results']) > 0:
        top_result = results['results'][0]

    if 'id' in top_result: 
        util.info("got id of " + top_result['display_name']) # POSSBUG: multiple journals of same name
        return top_result['id'], top_result['works_count']
    else: 
        print("No results found.")
        return FAIL

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
        for work in results:
            title = work['display_name']
            if util.valid_title(title):
                parseDetails.parse_work(work, data)
            
        page += 1
        # end loop when either there are no more results on the requested page 
        # or the next request would exceed 10,000 results
        page_size = page_with_results['meta']['per_page']
        has_more_pages = len(results) == page_size
        fewer_than_10k_results = page_size * page <= 10000
        
        if page % 5 == 0:
            util.info("iterating through pages: on page " + str(page))

def display_data(data):
    """ Displays visualizations and/or writes data csv as dictated by commandline args
        :param data: filled Data object with config fields write_csv, maps, gender
    """
    dict = {'author' : data.authors, 
            'title' : data.titles, 
            'year' : data.years,
            'institution' : data.institution_names, 
            'latitude' : data.latitudes, 
            'longitude' : data.longitudes}
        
    if data.config.abstracts: 
        dict['abstract'] = data.abstracts

    if data.config.gender: 
        if not data.config.restore_saved: # TODO: migrate this out of display_data bc it's calculation
            data.gender_strings, data.gender_data = gender.predict_gender(data.authors, data.years)
            dict['predicted gender'] = data.gender_strings
        gender.plot_gender_by_year(data.gender_data)

    df = pd.DataFrame(dict)
    util.info(df.head())

    if data.config.csv: 
        util.info("Writing csv...")
        df.to_csv("../data/data.csv")

    if data.config.maps:
        util.info("Mapping points...")
        map_dict = {'latitude' : data.latitudes, 'longitude' : data.longitudes} 
        map_df = pd.DataFrame(map_dict)
        df = map_df.groupby(['longitude', 'latitude']).size().reset_index(name='counts')
        map_points(df, 'world')
        util.info("Maps created!")

if __name__ == "__main__":
    args = parseArguments()
    main(args)
 