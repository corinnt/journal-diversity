
import requests
import pandas as pd
import numpy as np
from tqdm import tqdm

import gender

from gender import GenderData
from map import map_points
from multiRequests import multithr_iterate

import util

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
        #self.gender_data = None

        self.latitudes = []
        self.longitudes = []

        self.config = args
        self.id = None
        self.num_works = 0

    def iterate_search(self, args):
        """
        :param data: Data object - precondition empty / freshly instantiated
        :param source_id: string - OpenAlex ID of the source to analyze
        """
        # POSSBUG self is not empty

        # only get these fields for items retrieved:
        fields = 'display_name,authorships,concepts,publication_year,abstract_inverted_index'

        # filter items retrieved by year:
        search_filters = 'locations.source.id:' + self.id
        if args.start_year:
            search_filters += ',publication_year:>' + str(args.start_year - 1)
        if args.end_year: 
            search_filters += ',publication_year:<' + str(args.end_year + 1)

        works_query_with_page = 'https://api.openalex.org/works?select=' + fields + '&filter=' + search_filters + '&page={}&mailto=' + args.email
        page = 1
        has_more_pages = True
        fewer_than_10k_results = True
        institution_id_batches, author_id_batches = [], []
        while has_more_pages and fewer_than_10k_results:
            # set page value and request page from OpenAlex
            url = works_query_with_page.format(page)
            page_with_results = requests.get(url).json()
            # loop through page of results
            results = page_with_results['results']
            for work in results:
                title = work['display_name']
                if util.valid_title(title):
                    authorship_list = self.add_work(work)
                    institution_batch, author_batch = self.add_authorship(authorship_list)
                    institution_id_batches.append(institution_batch)
                    author_id_batches.append(author_batch)
            page += 1
            # end loop when either there are no more results on the requested page 
            # or the next request would exceed 10,000 results
            page_size = page_with_results['meta']['per_page']
            has_more_pages = len(results) == page_size
            fewer_than_10k_results = page_size * page <= 10000
            
            #NOTE: TOGGLE FOR TEST
            if page == 5:
                has_more_pages = False
            if page % 5 == 0:
                util.info("iterating through pages: on page " + str(page))
        
        return institution_id_batches, author_id_batches
    
    def add_work(self, work):
        """ Given a Work object and Data object to fill, adds title, year, and abstract to self, 
            and returns list of Authorship objects
            :param work: single Work object from OpenAlex
        """
        title = work['display_name']
        if not title: title = 'NA'
        self.titles.append(title)

        year = str(work['publication_year'])
        if not year: year = 'NA'
        self.years.append(year)

        if self.config.abstracts:
            inverted_index = work['abstract_inverted_index']
            words = util.decode_inverted(inverted_index)
            text = ' '.join(words)
            self.abstracts.append(text)
            
        authorship_list = work['authorships']
        return authorship_list
        #concepts_list = work['concepts']
        #parse_concepts(concepts_list, data)
        
    def add_concepts(self, concepts):
        """
            :param concepts: list of dehydrated Concept objects from OpenAlex
        """
        if not concepts:
            self.concepts.append('NA')
            return
        concept_string = ""
        for concept in concepts:
            if concept['score'] > 0.3:
                concept_string += concept['display_name'] + "; "
        self.concepts.append(concept_string)

    def add_authorship(self, authorships):
        """ Adds Authorship information to Data object - names of authors, their institutions
            Returns lists of institution IDs and author IDs to parse for geodata.
            The first Author in the list whose institution has geodata will be mapped. 
            Args: 
                authorships: list[OpenAlex Authorship]
        """
        if not authorships:
            self.authors.append('NA')
            self.institution_names.append('NA')
            #self.latitudes.append(np.nan)
            #self.longitudes.append(np.nan)
            return [], []

        author_names, institution_names, institution_ids, author_ids = [], [], [], []
        #mapped = False
        for i, authorship in enumerate(authorships):
            author_names.append(authorship['author']['display_name'])
            author_ids.append(authorship['author']['id'])
            for institution in authorship['institutions']:
                institution_names.append(institution['display_name'])
                institution_ids.append(institution['id'])
                #institution_ids.append(institution_id)
                #if not mapped and institution_id:              # will add longitude and latitude of first institution with geodata
                #    mapped, institution_name = self.parse_geodata(institution_id)
            #if not mapped and author_id:
            #    mapped, institution_name = self.alternate_geodata(author_id)
        author_string = util.namelist2string(author_names)
        institution_string = util.namelist2string(institution_names)
        self.authors.append(author_string) 
        self.institution_names.append(institution_string)
  
        return institution_ids, author_ids                       
        #if not mapped:
        #    self.latitudes.append(np.nan)
        #    self.longitudes.append(np.nan)

    def add_all_geodata(self, institution_ids, author_ids):
        """ Given a list of OpenAlex Institution IDs and Author IDs,
            sets the Data object's latitudes and longitudes list to the 
            results 
            # TODO: documentation
        """
        #latitudes, longitudes = multithr_iterate(zip(institution_ids, author_ids), 
        values = multithr_iterate(list(zip(institution_ids, author_ids)), 
                                                parse_work_geodata, 
                                                batch_size=1, max_workers=5)
        print("VALUES: " + str(values))
        lats, longs = values
        self.latitudes = lats
        self.longitudes = longs

    def display_data(self):
        """ Displays visualizations and/or writes data csv as dictated by commandline args.
            Currently also does gender prediction calls # TODO fix gender portion
        """
        dict = {'author' : self.authors, 
                'title' : self.titles, 
                'year' : self.years,
                'institution' : self.institution_names, 
                'latitude' : self.latitudes, 
                'longitude' : self.longitudes}
            
        if self.config.abstracts: 
            dict['abstract'] = self.abstracts

        if self.config.gender: 
            if not self.config.restore_saved: # TODO: migrate this out of display_data bc it's calculation
                ordered_gender_tuples = gender.predict_gender(self.authors)
                gender_strings = util.reformat_as_strings(ordered_gender_tuples)
                dict['predicted gender'] = gender_strings
            #gender_data.plot_gender_by_year() # TODO: fix gender plots

        df = pd.DataFrame(dict)
        util.info(df.head())

        if self.config.csv: 
            util.info("Writing csv...")
            df.to_csv("../data/data.csv")

        if self.config.maps:
            util.info("Mapping points...")
            map_dict = {'latitude' : self.latitudes, 'longitude' : self.longitudes} 
            map_df = pd.DataFrame(map_dict)
            df = map_df.groupby(['longitude', 'latitude']).size().reset_index(name='counts')
            map_points(df, 'world')
            util.info("Maps created!")

def parse_work_geodata(institutions_and_authors, i):
    """ 
    """
    print("institution_author_batch: " + str(institutions_and_authors[0]))
    institution_batch, author_batch = institutions_and_authors[0]
    latitude, longitude = np.nan, np.nan
    for institution in institution_batch:
        latitude, longitude = institution_id_geodata(institution)
        if latitude != np.nan: 
            print ("institution geodata.\tlatitude: " + str(latitude) + "\tlongitude: " + str(longitude) + "\ti: " + str(i))
            return latitude, longitude, i
    for author in author_batch:
        latitude, longitude = author_id_geodata(author)
        if latitude != np.nan: 
            print ("alternate geodata.\tlatitude: " + str(latitude) + "\tlongitude: " + str(longitude) + "\ti: " + str(i))
            return latitude, longitude, i
    print ("no geodata.\tlatitude: " + str(latitude) + "\tlongitude: " + str(longitude) + "\ti: " + str(i))
    return latitude, longitude, i
        # none of the institutions or authors had geodata
        
def institution_id_geodata(id):
    """ Given an Institution ID, adds 
        :param id: - string ID of Institution to check for geodata
        :returns bool: - True if successfully added coordinates
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