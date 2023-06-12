import pickle

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

def decode_inverted(inverted_index, data):
    """ Converts an inverted index to plain text and adds it to Data's list of abstracts
        :param inverted_index: dict of word : [indices] representing an abstract
        :param data: partially filled Data objedct
    """
    if not inverted_index:
        data.abstracts.append('NA')
        return
    word_index = [] 
    for k, v in inverted_index.items():
        for index in v:
            word_index.append([k, index])

    sorted_tuples = sorted(word_index, key = lambda x : x[1])
    words = [word[0] for word in sorted_tuples]
    words = ' '.join(words)
    #add to data object
    data.abstracts.append(words)

def predict_gender(authors):
    """ TODO: need to extract first names not full names
        might want to add this functionality while they're still lists too
    """
    genders = []
    batch = []
    BATCH_SIZE = 10
    authors_remaining = len(authors)
    batch_start = 0
    while authors_remaining:
        if authors_remaining > BATCH_SIZE:
            batch = authors[batch_start:BATCH_SIZE]
        else: 
            batch = authors[batch_start:]

        # genders += batch request
        
        batch_start += BATCH_SIZE
        authors_remaining -= BATCH_SIZE

    return genders