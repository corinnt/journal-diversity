from operator import invert
import pickle
import requests

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

    return list(uniques)

def openalex_request(url):
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

def valid_title(title):
    """ 
        Given a title, returns true if the title is not one of the "issue components"
            :param title: prospective title 
            :returns bool: True if valid
    """
    return title and\
            title != "Front Matter" and \
            title != "Back Matter" and \
            title != "Front Cover" and \
            title != "Back Cover" and \
            title != "Volume Information" and\
            "the following abbreviations are used in this issue" not in title.lower()

def pickle_data(data):
    """ Takes in populated Data object.
        Writes pickled files to data/pickled_data. 
    """
    destination = "../data/pickled_data"
    pickled_data = open(destination, "wb")
    pickle.dump(data, pickled_data)

def unpickle_data(path):
    """ Takes in filepath to the pickled Data object from a previous run
        Returns the unpickled Data object.
    """
    pickled_data = open(path, "rb")
    data = pickle.load(pickled_data)
    return data

def deNone(name):
    if not name: return 'NA' 
    else: return name

def namelist2string(names):
    """ Converts a list of strings to a single string w/ itmes sepaarated by '; ' 
        None values included as 'NA' to maintain length/indicate absence
    """
    names = [deNone(name) for name in names]
    if len(names) > 0: 
        string = '; '.join(names)
    else: string = 'NA'
    return string

def reformat_as_strings(ordered_tuples):
    """ Given a list of tuples pairing strings to indices,
    returns as a list of strings with strings of same index joined by namelist2string
    :param ordered_tuples: list[(str, int)]
    :returns strings: list[str]
    """
    if not ordered_tuples: return []
    strings = []
    #ordered_tuples.sort(key = lambda pair : pair[1]) already sorted?
    prev_index, mini_list = 0, []
    for item, index in ordered_tuples:
        if prev_index is not index:
            single_string = namelist2string(mini_list) #convert accrued list of names to string
            strings.append(single_string)
            prev_index = index
            mini_list = [item]
        else:
            mini_list.append(item)
            prev_index = index
    final_string = namelist2string(mini_list) #sweep up the final string that just got added to mini_list
    strings.append(final_string)
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
            :param inverted_index: dict of word : [indices] representing an abstract
            :param return_tuples: default False, when True, returns list of tuples not list of strings
            :returns list: default list of ordered words, ^ may be list of (str, int) tuples sorted by int
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
