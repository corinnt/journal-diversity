import util

def predict_gender(authors):
    """ Given a list of authors, returns a list of their predicted genders (via Genderize API)
        :param authors: list[str] of author full names
        :returns genders: list[str] of predicted genders
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
        #TODO:[next] replace w/ Genderize request
        batch_genders = [name for name in batch_names]
        batch_dict = {name : gender for name, gender in zip(batch_names, batch_genders)}
        genders_dict.update(batch_dict)
        batch_start += BATCH_SIZE
        authors_remaining -= BATCH_SIZE
    ordered_names = util.decode_inverted(inverted_index, return_tuples=True)
    # convert ordered names to ordered corresponding genders
    ordered_genders = [(genders_dict[name], i) for name, i in ordered_names]
    gender_strings = util.reformat_as_strings(ordered_genders)
    return gender_strings

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

        

