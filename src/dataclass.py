import requests
import pandas as pd
import numpy as np
from tqdm import tqdm
from scipy import stats as st

import util
from config import Config
from geodata import parse_work_geodata, map_points
from multiRequests import multithr_iterate, api_get, api_post

def get_journal(journal_name, email):
        """ Returns the OpenAlex Source object of the top result for the input journal name

            Args:
                journal_name: str name of journal for which to search 
            Returns:
                json - OpenAlex Source object for top match in database
        """    
        url = "https://api.openalex.org/sources?search=" + journal_name + '&mailto=' + email
        results = api_get(url)
        if len(results['results']) > 0: 
            top_result = results['results'][0]
            util.info("\nFound {}.".format(top_result['display_name']))
            return top_result
        else:
            raise Exception("No results found for journal " + journal_name + " in OpenAlex database.")

class Data():
    def __init__(self, args, config_json):
        self.analysis = args
        self.config = Config(config_json)

        journal = get_journal(args.journal_name, self.config.email)
        self.source_id = journal['id']
        self.num_works = journal['works_count']
        self.analysis.journal_name = journal['display_name']

        self.titles = []
        self.authors = []
        self.abstracts = []
        self.years = []
        self.institution_names = []

        self.latitudes = []
        self.longitudes = [] 

    def iterate_search(self):
        """ 
        Pages over Works for journal, populating titles, authors, publication years, and abstracts. 

        Args:
            data: Data object - precondition empty / freshly instantiated
            source_id: string - OpenAlex ID of the source to analyze
        Returns:
            (list[list[institution IDs]], list[list[author IDs]]) -
            for each work in journal, lists of affiliated institution and author IDs
        """
        # only get these fields for items retrieved:
        fields = 'display_name,authorships,concepts,publication_year,abstract_inverted_index'
        # filter items retrieved by year:
        search_filters = 'locations.source.id:' + self.source_id
        if self.analysis.start_year:
            search_filters += ',publication_year:>' + str(self.analysis.start_year - 1)
        if self.analysis.end_year: 
            search_filters += ',publication_year:<' + str(self.analysis.end_year + 1)
       
        if self.analysis.sample_size:
            sample_size = str(self.analysis.sample_size) 
            seed = str(42)
            sampling = 'sample='+ sample_size + '&seed='+ seed
        else:
            sampling = ''
        field_selection = 'select=' + fields
        filtering = 'filter=' + search_filters

        works_query_with_page = ('https://api.openalex.org/works?' +
                                sampling + '&' + \
                                field_selection + '&' + \
                                filtering + '&page={}&mailto=' + self.config.email)
        page = 1
        has_more_pages = True
        fewer_than_10k_results = True
        institution_id_batches, author_id_batches = [], []
        while has_more_pages and fewer_than_10k_results:
            # set page value and request page from OpenAlex
            url = works_query_with_page.format(page)
            page_with_results = api_get(url)
            # loop through page of results
            results = page_with_results['results']
            for work in results:
                title = work['display_name']
                if util.valid_title(title):
                    authorship_list = self.add_work_basics(work)
                    institution_ids, author_ids = self.add_authorship(authorship_list)
                    institution_id_batches.append(institution_ids)
                    author_id_batches.append(author_ids)
            page += 1
            # end loop when either there are no more results on the requested page 
            # or the next request would exceed 10,000 results
            page_size = page_with_results['meta']['per_page']
            has_more_pages = len(results) == page_size
            fewer_than_10k_results = page_size * page <= 10000
            
            if page % 5 == 0:
                util.info("On page " + str(page) + ".")
        
        return institution_id_batches, author_id_batches
    
    def populate_additional_data(self, institution_ids, author_ids):
        """ Given list of institution IDs and list of author IDs, populates the Data object
            with geodata if indicated by commandline arguments. 
        """
        if self.analysis.maps:
            self.add_geodata(institution_ids, author_ids) 
     
    def add_work_basics(self, work):
        """ Given a Work object and Data object to fill, adds title, year, and abstract to self, 
            and returns list of Authorship objects
            Args:
                work: single OpenAlex Work object
            Returns:
                authorship_list : list of the work's associated Authorship objects
        """
        title = work['display_name']
        if not title: title = 'NA'
        self.titles.append(title)

        year = str(work['publication_year'])
        if not year: year = 'NA'
        self.years.append(year)

        if self.analysis.abstracts:
            inverted_index = work['abstract_inverted_index']
            words = util.decode_inverted(inverted_index)
            text = ' '.join(words)
            self.abstracts.append(text)
            
        authorship_list = work['authorships']
        return authorship_list

    def add_authorship(self, authorships):
        """ Given list of OpenAlex Authorship json for one Work,
            adds Authorship information to Data object - names of authors, their institutions.
            Returns lists of institution IDs and author IDs to parse for geodata.
            The first Author in the list whose institution has geodata will be mapped. 
            Args: 
                authorships: list[OpenAlex Authorship]
        """
        if not authorships:
            self.authors.append('NA')
            self.institution_names.append('NA')
            return [], []
        author_names, institution_names, institution_ids, author_ids = [], [], [], []
        for authorship in authorships:
            author_names.append(authorship['author']['display_name'])
            author_ids.append(authorship['author']['id'])
            for institution in authorship['institutions']:
                institution_names.append(institution['display_name'])
                institution_ids.append(institution['id'])

        author_string = util.namelist2string(author_names)
        institution_string = util.namelist2string(institution_names)
        self.authors.append(author_string) 
        self.institution_names.append(institution_string)
  
        return institution_ids, author_ids                       

    def add_geodata(self, institution_ids, author_ids):
        """ Given a list of OpenAlex Institution IDs and Author IDs,
            sets the Data object's latitudes and longitudes list to the results 
            # TODO: documentation
        """
        util.info("Retrieving geodata...")      
        results = multithr_iterate(list(zip(institution_ids, author_ids)), 
                                                parse_work_geodata, 
                                                batch_size=1, max_workers=2, tuples=True) #OpenAlex rate limiter can't handle workers > 2

        self.latitudes = [result[0] for result in results]
        self.longitudes = [result[1] for result in results]

    def print_stats(self):
        institution_dict = {}
        for group in self.institution_names:
            for institution in list(set(group.split(';'))): # unique institutions for a work
                if institution != 'NA':
                    util.increment(institution, institution_dict)
        ranked_institutions = list(institution_dict.items())
        ranked_institutions.sort(key = lambda kv : kv[1], reverse=True) 

        print("\n{} Summary".format(self.analysis.journal_name))
        print("Total Works Count: {}".format(self.num_works))
        print("Works sampled: {}".format(len(self.titles)))
        print("Institutions with most publications:")        
        for inst in ranked_institutions[:5]:
            print("     {}, {} publications".format(inst[0].strip(), inst[1]))
                             
    def display_data(self):
        """ Displays visualizations and writes data CSV as dictated by commandline args.
        """
        dict = {'author' : self.authors, 
                'title' : self.titles, 
                'year' : self.years,
                'institution' : self.institution_names}
        
        if self.analysis.abstracts: 
            dict['abstract'] = self.abstracts
        
        if self.analysis.maps:
            dict['latitude'] = self.latitudes
            dict['longitude'] = self.longitudes

        df = pd.DataFrame(dict)
        util.info(df.head())

        util.info("Writing csv...")
        df.to_csv(self.config.csv)

        if self.analysis.maps:
            util.info("Mapping points...")
            map_dict = {'latitude' : self.latitudes, 'longitude' : self.longitudes} 
            map_df = pd.DataFrame(map_dict)
            df = map_df.groupby(['longitude', 'latitude']).size().reset_index(name='counts')
            map_points(df, self.config.map)
            util.info("Map created at " + self.config.map + ".")
