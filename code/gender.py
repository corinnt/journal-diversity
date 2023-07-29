import util
from multiRequests import multithr_iterate
import pandas as pd
import matplotlib.pyplot as plt
import os




class GenderData():
    def __init__(self, gender_tuples, years):
        """Given a list of tuples of (gender, index) and list of years,
            populated a GenderData object with [[gender, gender], [gender], ...] and years"""
        gender_tuples.sort(key = lambda pair : pair[1]) #already sorted?
        grouped_gender_tuples = util.group_tuples(gender_tuples)
        self.genders : list[list] = [genders for genders, i in grouped_gender_tuples]
        self.years : list[int] = years
        assert len(self.genders) == len(self.years)

    def plot_gender_by_year(self):
        """ Currently *not* functional
            :param gender_data: GenderData object with dataframe of years and author genders
        """
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


def predict_gender(authors):
    """ Given a list of authors, returns a list of their predicted genders (via Genderize API)
        :param authors: list[str] of author full names
        :returns gender_strings: list[str] of predicted genders
        :returns genders_by_year: GenderData object to plot genders by year
    """
    first_names, inverted_index = full2first_names(authors)
    unique_names : list = util.unique(first_names)

    path = "../data/pickled_genders"
    if os.path.exists(path) and os.path.isfile(path):
        genders_dict = util.unpickle_data(path)
    else:
        genders_dict = get_genders_dict(unique_names)
        util.pickle_data(genders_dict, dst=path)

    ordered_names = util.decode_inverted(inverted_index, return_tuples=True)
    # convert ordered names to ordered corresponding genders
    ordered_gender_tuples = [(genders_dict[name], i) for name, i in ordered_names]
    return ordered_gender_tuples

def get_genders_dict(unique_names):
    """ Given a list of unique first names, returns a dict of names mapped to genders.
        Uses Genderize batch requests.
    """
    genders_dict = {}
    #batch_start, BATCH_SIZE = 0, 10
    #authors_remaining : int = len(unique_names)
    #while authors_remaining > 0:
    #    batch_names = []
    #    if authors_remaining > BATCH_SIZE:
    #        batch_names = unique_names[batch_start : batch_start + BATCH_SIZE]
    #    else: 
    #        batch_names = unique_names[batch_start:]
    #    batch_genders = genderize_request(batch_names)
    #    batch_dict = {name : gender for name, gender in zip(batch_names, batch_genders)}
    #    genders_dict.update(batch_dict)
    #    batch_start += BATCH_SIZE
    #    authors_remaining -= BATCH_SIZE
    genders = multithr_iterate(unique_names, genderize_request, batch_size=10)
    genders_dict = {name : gender for name, gender in zip(unique_names, genders)}

    return genders_dict

    multithr_iterate_ids(ids, )

def full2first_names(authors):
    """ Returns a list of first names found in the authors list and an inverted index indicating the name locations
        Args:    
            authors: list[str] st each str is a semicolon-separated list of one or more full names
        Returns:
            first_names: list[str] of unique first names (first approximated by first 'word' in each name)
            inverted_index: dict[name : list[indices]] mapping occurrences of each first name in original list of names
    """
    separator = ';'
    first_names = []
    inverted_index = {}
    for i, author_group in enumerate(authors):
        full_names = author_group.split(separator)
        for name in full_names:
            segments = name.split()
            first_name = segments[0]
            first_names.append(first_name)
            util.add_to_inverted_index(first_name, i, inverted_index)
    return first_names, inverted_index

def genderize_request(name_list):
    url_base = 'https://api.genderize.io/?'
    query = "" 
    for name in name_list:
        query += 'name[]=' + name + '&'
    query = query[:-1] # drop string's final '&'
    predictions = util.api_request(url_base + query)
    if not predictions: return []
    genders = [pred['gender'] for pred in predictions]
    return genders