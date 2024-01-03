import pandas as pd
import matplotlib.pyplot as plt
import os
import pprint
from map import map_points

import util
from dataclass import Data
from multiRequests import multithr_iterate

"""
class GenderData():
    def __init__(self, gender_tuples, years):
        Given a list of tuples of (gender, index) and list of years,
            populates a GenderData object with [[gender, gender], [gender], ...] and years
        gender_tuples.sort(key = lambda pair : pair[1]) #already sorted?
        grouped_gender_tuples = util.group_tuples(gender_tuples)
        self.genders : list[list] = [genders for genders, _ in grouped_gender_tuples]
        self.years : list[int] = years
        assert len(self.genders) == len(self.years)

    def plot_gender_by_year(self):
         NOTE Currently not functional
            :param gender_data: GenderData object with dataframe of years and author genders
        
    # TODO: test/fix gender plotting
        dict = {'year' : self.years, 
                'gender' : self.genders}
        df = pd.DataFrame(dict)
        df['year'] = pd.to_datetime(df['year'], format='%Y')
        #df_grouped = df.groupby('year')['gender'].value_counts().unstack()
        #df_resampled = df.resample('5Y', on='year').count()

        # Resample the data using a 5-year frequency and separate by gender
        df_resampled = df.groupby('gender').resample('5Y', on='year').value_count().unstack()
        df_resampled.plot(kind='line', marker='o', figsize=(10, 6), color=['red', 'blue'])
        #df_grouped.plot(kind='line', marker='o', figsize=(10, 6), color=['red', 'blue'])
        plt.xlabel('Year')
        plt.ylabel('Number Authors')
        plt.title('Number of Male and Female Authors over Time')
        plt.legend()
        plt.grid(True)
        plt.savefig("../data/gender-over-time.png")
        plt.show()
"""
############################################################################################

class GenderData(Data):
    def __init__(self, args, config_json):
        super().__init__(args, config_json)
        #gender_strings: list[] of predicted genders of Work authors
        #  s.t. each string is ';'-separated genders from same Work
        self.gender_strings = []
        self.genders = []

    def predict_genders(self, restore_saved=False):
        """ Given a data object, populates the gender_strings with predicted genders, 
            and returns 
            (via Namsor API)
            Args:
                authors: list[str] of author full names
                restore_saved: read from existing file rather than Namsor requests
            Returns: 
                
        """        
        first_names, inverted_index = full2first_names(self.authors)
        unique_names = util.unique(first_names)
        genders_dict = {}
        if restore_saved and os.path.exists(self.config.gender_src):
            genders_dict = util.unpickle_data(self.config.gender_src)
        else:
            genders_dict = self.get_genders_dict(unique_names)
            util.pickle_data(genders_dict, dst=self.config.gender_dst)

        ordered_name_tuples = util.decode_inverted(inverted_index, return_tuples=True)
        ordered_gender_tuples = [(genders_dict[name], i) for name, i in ordered_name_tuples]

        genders = [list for list, _ in util.group_tuples(ordered_gender_tuples)]
        self.genders = genders

        gender_strings : list[str] = [util.namelist2string(list) for list in genders]
        self.gender_strings = gender_strings

    def get_genders_dict(self, unique_names):
        """ 
        Given a list of unique first names, returns a dict of names mapped to genders. 
        Uses Namsor batch requests.
        """
        key_and_names = (self.config.gender_apikey, unique_names)
        genders = multithr_iterate(key_and_names, namsor_request, batch_size=10, max_workers=10)
        genders_dict = {name : gender for name, gender in zip(unique_names, genders[0][0])}
        return genders_dict
    
    def populate_additional_data(self, institution_ids, author_ids):
        """ Given list of institution IDs and list of author IDs, populates the GenderData object
            with gender data, as well as geodata if indicated by commandline arguments. 
        """
        self.predict_genders()

        if self.analysis.maps:
            self.add_geodata(institution_ids, author_ids) 

    def display_data(self):
        """ Displays visualizations and/or writes data csv as dictated by commandline args.
            Currently also does gender prediction calls 
        """
        dict = {'author' : self.authors, 
                'title' : self.titles, 
                'year' : self.years,
                'institution' : self.institution_names, 
                'predicted gender' : self.genders}
        if self.analysis.abstracts: 
            dict['abstract'] = self.abstracts
        if self.analysis.maps:
            dict['latitude'] = self.latitudes, 
            dict['longitude'] = self.longitudes

        df = pd.DataFrame(dict)
        util.info(df.head())

        util.info("Writing csv...")
        df.to_csv(self.config.csv)

        self.plot_gender_by_year()

        if self.analysis.maps:
            util.info("Mapping points...")
            map_dict = {'latitude' : self.latitudes, 'longitude' : self.longitudes} 
            map_df = pd.DataFrame(map_dict)
            df = map_df.groupby(['longitude', 'latitude']).size().reset_index(name='counts')
            map_points(df, self.config.map)
            util.info("Map " + self.config.map + " created!")

    def plot_gender_by_year(self, bucket_size=5):
        """ Given GenderData object, generates line plot of genders of authors over time.
                
        """
        gender_dict, year_buckets = {}, [] #genders maps (gender, year) pairs to counts of occurrences
        for gender_lst, year in zip(self.genders, self.years):
            bucket = (int(year) // bucket_size) * bucket_size
            year_buckets.append(bucket)
            for gender in gender_lst:
                util.increment((gender, bucket), gender_dict)

        dict = {'year': sorted(list(set(year_buckets))), 
                'male': [], 
                'female': []}

        for gender in ['male', 'female']:
            for year in dict['year']:
                if (gender, year) in gender_dict:
                    dict[gender].append(gender_dict[(gender, year)])
                else:
                    dict[gender].append(0)     

        df = pd.DataFrame(dict)
        df.sort_values(by='year', ascending=True)

        plt.plot(df['year'], df['female'], marker='o', label='Female', color='red')
        plt.plot(df['year'], df['male'], marker='o', label='Male', color='blue')

        plt.xlabel('Year')
        plt.ylabel('Number Authors')
        plt.title('Number of Male and Female Authors over Time')
        plt.xticks(df['year'])
        plt.legend()
        plt.grid(True)
        plt.savefig(self.config.gender_plot)

def full2first_names(authors):
    """ 
    Returns a list of first names found in the authors list and an inverted index indicating the name locations.
        Args:    
            authors: list[str] st each str is a semicolon-separated list of one or more full names
        Returns:
            first_names: list[str] of unique first names (first approximated by first 'word' in each name)
            inverted_index: dict[name : list[indices]] mapping occurrences of each first name in original list of names
    """
    separator = ';'
    first_names, inverted_index = [], {}
    for i, author_group in enumerate(authors):
        full_names = author_group.split(separator)
        for name in full_names:
            try: 
                first_name = name.split()[0]
                first_names.append(first_name)
                util.add_to_inverted_index(first_name, i, inverted_index)
            except: 
                pass
    return first_names, inverted_index

def namsor_request(apikey_and_names, i):
    """ 
    Given a batch list of first names and the index of the batch in the larger list,
    returns the list of corresponding genders and the batch index
    TODO: docs 
    """
    #print(apikey_and_names)
    apikey, name_list = apikey_and_names
    url = "https://v2.namsor.com/NamSorAPIv2/api2/json/genderBatch"
    name_queries = [{"id": id, "firstName": name} for id, name in enumerate(name_list)]
    payload = {"personalNames": name_queries}
    headers = headers = {
        "X-API-KEY": apikey,
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    response = util.api_post(url, payload=payload, headers=headers)
    if not response: return [] # error occurred decoding Response
    genders = [(prediction['likelyGender']) for prediction in response['personalNames']]
    return genders, i

