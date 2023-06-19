from ast import NamedExpr
from operator import invert

import util

def predict_gender(authors):
    """ 

        
    """
    BATCH_SIZE = 10
    batch_start = 0
    genders_dict = {}

    first_names, inverted_index = first_names(authors)
    unique_names = util.unique(first_names)
    
    authors_remaining = len(unique_names)
    while authors_remaining > 0:
        batch_names = []
        if authors_remaining > BATCH_SIZE:
            batch_names = unique_names[batch_start:BATCH_SIZE]
        else: 
            batch_names = unique_names[batch_start:]

        #TODO:[eventual] fix w/ request
        batch_genders = [name for name in batch_names]

        batch_dict = {name : gender for name, gender in zip(batch_names, batch_genders)}
        genders_dict.update(batch_dict)

        batch_start += BATCH_SIZE
        authors_remaining -= BATCH_SIZE
    #TODO: fix ordered names by using reformat as string and recording/retrieving the indices when returing from inverted_index
    sorted_tuples = util.decode_inverted(inverted_index, return_tuples=True)
    ordered_names = [] # fix

    genders = [genders_dict[name] for name in ordered_names]

    return genders

def first_names(authors):
    """ Returns a list of first names found in the authors list and an inverted index indicating the name locations
        :param authors: list[str] st each str is one or more semicolon-separated full names
        :returns first_names: list[str] of unique first names (first approximated by first 'word' in each name)
        :return inverted_index: dict[name : list[indices]] mapping occurrences of each first name in original list of names
    """
    separator = ';'
    first_names = []
    for author_group in authors:
        full_names = author_group.split(separator)
        for name in full_names:
            segments = name.split()
            first_name = segments[0]
            first_names.append(first_name)
           
    return first_names, inverted_index

        

