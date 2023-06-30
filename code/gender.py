import util

import pandas as pd
import matplotlib.pyplot as plt

class GenderData():
    def __init__(self, gender_tuples, sparse_years):
        genders = []
        years = []
        print("gender_tuples: " + str(gender_tuples))
        print("sparse_years: " + str(sparse_years))
        if gender_tuples:
            gender_tuples.sort(key = lambda pair : pair[1]) #already sorted?
            for gender, index in gender_tuples:
                genders.append(gender)
                years.append(sparse_years[index])
        else: print("Issue with GenderData init")
        self.genders = genders
        self.years = years

def predict_gender(authors, years):
    """ Given a list of authors, returns a list of their predicted genders (via Genderize API)
        :param authors: list[str] of author full names
        :returns gender_strings: list[str] of predicted genders
        :returns genders_by_year: GenderData object to plot genders by year
    """
    batch_start, BATCH_SIZE = 0, 10
    genders_dict = {}

    first_names, inverted_index = full2first_names(authors)
    unique_names : list = util.unique(first_names)

    authors_remaining : int = len(unique_names)
    while authors_remaining > 0:
        batch_names = []
        if authors_remaining > BATCH_SIZE:
            batch_names = unique_names[batch_start:batch_start + BATCH_SIZE]
        else: 
            batch_names = unique_names[batch_start:]
        batch_genders = genderize_request(batch_names)
        batch_dict = {name : gender for name, gender in zip(batch_names, batch_genders)}
        genders_dict.update(batch_dict)
        batch_start += BATCH_SIZE
        authors_remaining -= BATCH_SIZE
    ordered_names = util.decode_inverted(inverted_index, return_tuples=True)
    # convert ordered names to ordered corresponding genders
    ordered_genders = [(genders_dict[name], i) for name, i in ordered_names]
    genders_by_year = GenderData(ordered_genders, years)
    gender_strings = util.reformat_as_strings(ordered_genders)
    return gender_strings, genders_by_year

def full2first_names(authors):
    """ Returns a list of first names found in the authors list and an inverted index indicating the name locations
        :param authors: list[str] st each str is one or more semicolon-separated full names
        :returns first_names: list[str] of unique first names (first approximated by first 'word' in each name)
        :return inverted_index: dict[name : list[indices]] mapping occurrences of each first name in original list of names
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
    query = query[:-1]
    predictions = util.api_request(url_base + query)
    if not predictions: return []
    genders = [pred['gender'] for pred in predictions]
    return genders

def plot_gender_by_year(gender_data):
    """
        :param gender_data: GenderData object
    """
    years = gender_data.years
    genders = gender_data.genders

    dict = {'year' : years, 
            'gender' : genders}

    df = pd.DataFrame(dict)
    df['year'] = pd.to_datetime(df['year'], format='%Y')
    df_grouped = df.groupby('year')['gender'].value_counts().unstack()
    df_grouped.plot(kind='line', marker='o', figsize=(10, 6), color=['red', 'blue'])
    plt.xlabel('Year')
    plt.ylabel('Number Authors')
    plt.title('Number of Male and Female Authors over Time')
    plt.legend()
    plt.grid(True)
    plt.show()
    plt.savefig("../data/gender-over-time.png")







