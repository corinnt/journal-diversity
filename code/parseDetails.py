import requests
import numpy as np
import util
import diversity

def parse_work(work, data):
    """
        :param work: single Work object from OpenAlex
        :param data: partially full Data object
    """
    title = work['display_name']
    if not title: title = 'NA'
    data.titles.append(title)

    year = str(work['publication_year'])
    if not year: year = 'NA'
    data.years.append(year)

    if data.config.write_abstracts:
        inverted_index = work['abstract_inverted_index']
        words = util.decode_inverted(inverted_index)
        text = ' '.join(words)
        data.abstracts.append(text)
        
    authorship_list = work['authorships']
    parse_authorship(authorship_list, data)

    #concepts_list = work['concepts']
    #parse_concepts(concepts_list, data)
        
def parse_concepts(concepts, data):
    """
        :param concepts: list of dehydrated Concept objects from OpenAlex
        :param data: partially full Data object
    """
    if not concepts:
        data.concepts.append('NA')
        return
    concept_string = ""
    for concept in concepts:
        if concept['score'] > 0.3:
            concept_string += concept['display_name'] + "; "
    data.concepts.append(concept_string)

def parse_authorship(authorships, data):
    """ Adds Authorship information (names of authors, their institutions, and the location of their institution) to Data object
        The first Author in the list whose institution has geodata will be mapped. 
        :param authorships: list of authorship objects from the OpenAlex API
        :param data: partially full Data object
    """
    if not authorships:
        data.authors.append('NA')
        data.institution_names.append('NA')
        data.latitudes.append(np.nan)
        data.longitudes.append(np.nan)
        return

    author_names = []
    institution_names = []
    mapped = False

    for authorship in authorships:
        institution_name = ""
        for institution in authorship['institutions']:
            institution_name = institution['display_name'] # need to add this name to string in case Work is already mapped
            institution_id = institution['id']
            if not mapped and institution_id:              # will add longitude and latitude of first institution with geodata
                mapped, institution_name = parse_geodata(institution_id, data)
            institution_names.append(institution_name)
        author_id = authorship['author']['id']

        if not mapped and author_id:
            mapped, institution_name = alternate_geodata(author_id, data)

        author_names.append(authorship['author']['display_name'])

    institution_string = util.namelist_to_string(institution_names)
    author_string = util.namelist_to_string(author_names)

    data.institution_names.append(institution_string)
    data.authors.append(author_string)                          

    if not mapped:
        data.latitudes.append(np.nan)
        data.longitudes.append(np.nan)

def parse_geodata(id, data):
    """
        :param id: - string ID of Institution to check for geodata
        :param data: - partially full Data object
        :returns bool: - True if successfully added coordinates
    """
    if not id: 
        util.info("Blank ID passed to parse_geodata")
        return False, ""

    url =  "https://api.openalex.org/institutions/" + id
    institution = util.openalex_request(url)
    if not institution: return False, 'NA'

    display_name = institution['display_name']
    if 'latitude' in institution['geo']:
        lat = institution['geo']['latitude']
        long = institution['geo']['longitude']
        data.latitudes.append(lat)
        data.longitudes.append(long)
        return True, display_name
    else:
        util.info("Geo information unavailable for " + display_name)
        return False, display_name

def alternate_geodata(id, data):
    """
        :param authorship: string id of Author to check for most recent institution's geodata
        :param data: partially full Data object    
        :return bool: returns True if successfully found institution/location info to Data
    """
    if not id: return False
    url =  "https://api.openalex.org/authors/" + id
    author = util.openalex_request(url)
    if not author: return False, 'NA'

    if author['last_known_institution']:
        institution_id = author['last_known_institution']['id']
        mapped, name = parse_geodata(institution_id, data)
        util.info("adding last known institution " + name)
        return mapped, "last known: " + name
    else:
        util.info("Last known institution unavailable.")
        return False, 'NA'

