import requests
from util import increment, decode_inverted
from diversity import info

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
        if inverted_index:
            decode_inverted(inverted_index, data)
        else:
            data.abstracts.append('NA')

    authorship_list = work['authorships']
    if authorship_list:
        parse_authorship(authorship_list, data)
    else:
        data.authors.append('NA')

    concepts_list = work['concepts']
    if concepts_list:
        parse_concepts(concepts_list, data)
    else:
        data.concepts.append('NA')

    
        
def parse_concepts(concepts, data):
    """
        :param concepts: list of dehydrated Concept objects from OpenAlex
        :param data: partially full Data object
    """
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
    author_string = ""
    for authorship in authorships:
        author_string += authorship['author']['display_name'] + "; "
        for institution in authorship['institutions']:
            code = institution['country_code']
            id = institution['id']
            if id: parse_geodata(id, data)
            increment(code, data.countries)
            increment(id, data.institutions)
            data.institution_ids.add(id)
    data.authors.append(author_string)

def parse_geodata(id, data):
    """
        :param id: - string ID of Institution to check for geodata
        :param data: - partially full Data object
    """
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
            increment((long, lat), data.coordinates)

    except requests.exceptions.RequestException as e:
        print("Error occurred:", e)
    except ValueError as e:
        print("Error decoding JSON:", e)