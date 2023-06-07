import pickle

def increment(key, dict):
    if key in dict:
        dict[key] += 1
    else:
        dict[key] = 1

def valid_title(title):
    """ 
        Given a title, returns true if the title is not 
            :param title: prospective title 
    """
    return title and\
            title != "Front Matter" and \
            title != "Back Matter" and \
            title != "Front Cover" and \
            title != "Back Cover"

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

def decode_inverted(inverted_index, data):
    """ Converts a dictionary of word : [indices] to plain text and adds it to Data's list of abstracts
        :param inverted_index: 
        :param data: 
    """
    if not inverted_index:
        data.abstracts.append('NA')
    else:
        word_index = [] 
        for k, v in inverted_index.items():
            for index in v:
                word_index.append([k, index])

        sorted_tuples = sorted(word_index, key = lambda x : x[1])
        words = [word[0] for word in sorted_tuples]
        words = ' '.join(words)
        data.abstracts.append(words)