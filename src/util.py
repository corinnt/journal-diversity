from operator import invert
import pickle
import requests
import json

VERBOSE = False
def info(text):
    global VERBOSE
    if VERBOSE:
        print(text)

def increment(key, dict):
    if key in dict:
        dict[key] += 1
    else:
        dict[key] = 1

def unique(duplicates):
    """ Given a list, return that list without duplicates
    """
    uniques = set()
    uniques.update(duplicates)
    uniques_list = list(uniques)
    return uniques_list

def foldl(base, fn, lst):
    result = base.copy()
    for item in lst:
        result = fn(result, item)
    return result

def load_config(file_path):
    """ Given a path to a config file, returns as JSON object. 
    """
    with open(file_path, "r") as f:
        config = json.load(f)
    return config

def api_get(url):
    """ Given a GET url, returns results or handles errors
        Args: 
            url: str - API request url
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        results = response.json()
    except requests.exceptions.RequestException as e:
        print("Error occurred:", e)
        return None
    except ValueError as e:
        print("Error decoding JSON:", e)
        return None
    return results

def api_post(url, payload, headers):
    """ Given a POST request, returns results or handles errors
        Args: 
            url: str - API Request url
            payload: json - payload to send in the body of the Request
            headers: Dictionary of HTTP Headers to send with the Request
    """
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        results = response.json()
    except requests.exceptions.RequestException as e:
        print("Error occurred:", e)
        return 
    except ValueError as e:
        print("Error decoding JSON:", e)
        return 
    return results 

def valid_title(title):
    """ 
        Given a title, returns true if the title is not one of the "issue components". 
        Args:
            title: str - prospective title 
        Returns:
            bool - True if valid
    """
    return title and\
            title != "Front Matter" and \
            title != "Back Matter" and \
            title != "Front Cover" and \
            title != "Back Cover" and \
            title != "Volume Information" and\
            "the following abbreviations are used in this issue" not in title.lower()

def pickle_data(data, dst="../data/pickled_data"):
    """ Given a data object, 
        writes pickled files to `dst`. 
    """
    pickled_data = open(dst, 'wb')
    pickle.dump(data, pickled_data)

def unpickle_data(src):
    """ Given the filepath to a pickled object,
        returns the unpickled Data object.
    """
    pickled_data = open(src, 'rb')
    data = pickle.load(pickled_data)
    return data

def deNone(name):
    if not name: return 'NA' 
    else: return name

def namelist2string(names):
    """ Converts a list of strings to a single string w/ items separated by '; ' 
        None values included as 'NA'. 
    """
    names = [deNone(name) for name in names]
    if len(names) > 0: 
        string = '; '.join(names)
    else: string = 'NA'
    return string

def group_tuples(tuples):
    """Given a list of tuples of (item, index),
        Returns a condensed + sorted list of tuples of ([items], unique_index)"""
    # Create a dictionary to mapping indices to a list of genders
    index_groups = {} 
    for item, index in tuples:
        if index not in index_groups:
            index_groups[index] = [item]
        else:
            index_groups[index].append(item)
    # Convert the dictionary items to a list of tuples
    grouped_tuples = [(items, index) for index, items in index_groups.items()]
    grouped_tuples.sort(key = lambda pair : pair[1]) #already sorted?
    #TODO just return the values at this point. 
    return grouped_tuples

def reformat_as_strings(ordered_tuples):
    """ Given a list of tuples pairing strings to indices,
    returns as a list of strings with strings of same index joined by namelist2string
    Args:
        ordered_tuples: list[(str, int)]
    Returns:
        strings: list[str] 
    """
    #if not ordered_tuples: return [] #TODO need to handle this explicitly?
    grouped_tuples : list[tuple(list, int)] = group_tuples(ordered_tuples)
    strings : list[str] = [namelist2string(names) for names, _ in grouped_tuples]
    return strings

            
def add_to_inverted_index(key, index, inverted_index):
    """ Given a key, index, and inverted_index, adds the key-index pair to the inverted index
            :param key: str to be added
            :param index: int index where the key occurs in the original text
            :param inverted_index: dict(str -> [indices])
            :returns None:
    """
    if key not in inverted_index:
        inverted_index[key] = [index]
    else:
        inverted_index[key].append(index)

def decode_inverted(inverted_index, return_tuples=False):
    """ Converts an inverted index to list of words in the correct order
            Args:
                inverted_index: dict of word : [indices] representing an abstract
                return_tuples: default False, when True, returns list of tuples not list of strings
            Returns:
                list[str] - list of words ordered by index, or list[(str, int)] sorted by index
    """
    if not inverted_index: return 'NA'

    word_index = [] 
    for word, indices in inverted_index.items():
        for index in indices:
            word_index.append([word, index])

    sorted_tuples = sorted(word_index, key = lambda x : x[1])
    if return_tuples: 
        return sorted_tuples
    words = [word[0] for word in sorted_tuples]
    return words