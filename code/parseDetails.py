import requests
import numpy as np
from util import increment, decode_inverted
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
        decode_inverted(inverted_index, data)
        
    authorship_list = work['authorships']
    parse_authorship(authorship_list, data)

    concepts_list = work['concepts']
    parse_concepts(concepts_list, data)
        
def parse_concepts(concepts, data):
    """
        :param concepts: list of dehydrated Concept objects from OpenAlex
        :param data: partially full Data object
    """
    if not concepts:
        data.concepts.append('NA')
    else:
        concept_string = ""
        for concept in concepts:
            if concept['score'] > 0.3:
                concept_string += concept['display_name'] + "; "
        data.concepts.append(concept_string)

def parse_authorship(authorships, data):
    """
        :param authorships: list of authorship objects from the OpenAlex API
        :param data: partially full Data object
    """
    if not authorships:
        data.authors.append('NA')
        data.institution_names.append('NA')
        data.latitudes.append(np.nan)
        data.longitudes.append(np.nan)
    else:
        author_string = ""
        institution_string = ""
        mapped = False
        for authorship in authorships:
            author_string += authorship['author']['display_name'] + "; "
            for institution in authorship['institutions']:
                id = institution['id']
                display_name = institution['display_name']
                if display_name: 
                    diversity.info("adding institution display_name: \'" + display_name + "\'")
                    institution_string += display_name + ";"
                else:
                    institution_string += "NA;"
                if not mapped and id: # will add longitude and latitude of first institution with geodata
                    mapped = parse_geodata(id, data)
        if not author_string: author_string += 'NA'
        if not institution_string: institution_string += 'NA'
        data.authors.append(author_string)
        data.institution_names.append(institution_string)

        if not mapped:
            for authorship in authorships:
                author_id = authorship['author']['id']
                mapped = alternate_geodata(author_id, data)
                if mapped: break
        if not mapped:
            data.latitudes.append(np.nan)
            data.longitudes.append(np.nan)

def parse_geodata(id, data):
    """
        :param id: - string ID of Institution to check for geodata
        :param data: - partially full Data object
        :returns bool: - True if successfully added coordinates
    """
    if not id: return False
    url =  "https://api.openalex.org/institutions/" + id
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        results = response.json()
        if 'latitude' in results['geo']:
            lat = results['geo']['latitude']
            long = results['geo']['longitude']
            data.latitudes.append(lat)
            data.longitudes.append(long)
            return True
        else:
            return False

    except requests.exceptions.RequestException as e:
        print("Error occurred:", e)
        return False
    except ValueError as e:
        print("Error decoding JSON:", e)
        return False

def alternate_geodata(id, data):
    """
        :param authorship: string id of Author to check for most recent institution's geodata
        :param data: partially full Data object    
        :return bool: returns True if successfully found institution/location info to Data
    """
    if not id: return False
    url =  "https://api.openalex.org/authors/" + id
    author = {}
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        author = response.json()
    except requests.exceptions.RequestException as e:
        print("Error occurred:", e)
        return False
    except ValueError as e:
        print("Error decoding JSON:", e)
        return False

    if author['last_known_institution']:
        institution_id = author['last_known_institution']['id']
        diversity.info("adding last known institution")
        return parse_geodata(institution_id, data)
    else:
        return False

