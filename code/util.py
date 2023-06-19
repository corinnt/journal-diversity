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

def unique(list):
    """ Given a list, return that list without duplicates
    """
    uniques = set()
    uniques.update(list)
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

def namelist_to_string(names):
    """ Converts a list of strings to a single string w/ itmes sepaarated by '; ' 
        None values included as 'NA' to maintain length/indicate absence
    """
    
    names = [deNone(name) for name in names]
    if len(names) > 0: 
        string = '; '.join(names)
    #elif len(names) == 1: string = names[0]
    else: string = 'NA'
    return string

def reformat_as_strings(genders, list_structure):
    """ Given a list of genders and a list of ints representing list lengths, 
    returns genders as a list of lists reformatted to the list_structure specifications
    
    """
    gender_strings = []
    list_structure.sort(key = lambda pair : pair[1])
    print(list_structure)

    old_index = list_structure[0][1]
    for name, index in list_structure:
        if old_index is not index: 
            mini_list = []
        else:
            mini_list.append(genders[base + n])
        single_string = namelist_to_string(mini_list)
        gender_strings.append(single_string)
        
    return gender_strings

def encode_inverted(list):
    """ TODO: documentation
    """
    if not list: 
        info("Encoded empty inverted_index.")
        return {}

    inverted_index = {name : [] for name in list}
    for name, i in enumerate(list):
        inverted_index[name].append(i)
    return inverted_index

def decode_inverted(inverted_index, return_tuples=False):
    """ Converts an inverted index to list of words in the correct order
        :param inverted_index: dict of word : [indices] representing an abstract
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
