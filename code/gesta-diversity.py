from operator import truediv
from readline import insert_text
import requests
import pandas as pd

from mailto import email # just a function that returns your email address
from map import map_points

class Data():
    def __init__(self):
        self.titles = []
        self.authors = []
        self.years = []

        self.countries = {}
        self.institutions = {}
        self.institution_ids = set()


def main(source_id):
    issn_l = "0016-920X"
    source_query = "https://api.openalex.org/sources/" + source_id
    data = Data()
    iterate_search(source_id, data)
    process_data(data)    
    # TODO: make protocol for what fields to query?
    # ie get institution ID, else get institution name and country, else get author name and country and year?

def increment(key, dict):
    if key in dict:
        dict[key] += 1
    else:
        dict[key] = 1

def valid_title(title):
    """
        :param title: prospective title
    """
    status = title and\
            title != "Front Matter" and\
            title != "Back Matter" and\
            title != "Front Cover" and\
            title != "Back Cover"
    return status

def parse_work(work, data):
    """
        :param work:
        :param data: a Data object to populate
    """
    title = work['display_name']
    if not title: title = 'NA'
    data.titles.append(title)

    year = str(work['publication_year'])
    if not year: 
        year = 'NA'
    data.years.append(year)

    authorship_list = work['authorships']
    if authorship_list:
        parse_authorship(authorship_list, data)
    else:
        data.authors.append('NA')

def parse_authorship(authorships, data):
    """
        :param authorships: list of authorship objects from the OpenAlex API
        :param data: Data object
    """
    author_string = ""
    for authorship in authorships:
        author_string += authorship['author']['display_name'] + " "
        for institution in authorship['institutions']:
            code = institution['country_code']
            id = institution['id']
            increment(code, data.countries)
            increment(id, data.institutions)
            data.institution_ids.add(id)
    data.authors.append(author_string)

def iterate_search(source_id, data):
    """
    :param source_id: string - OpenAlex ID of the source to analyze
    :param data: Data object
    """
    # only get name and authors for after 1999
    works_query_with_page = 'https://api.openalex.org/works?select=display_name,authorships,concepts,publication_year&filter=publication_year:>1999,locations.source.id:' + source_id + '&page={}&mailto=' + email()
    # get all Work info after 1999
    #works_query_with_page = 'https://api.openalex.org/works?select=display_name,authorships&page={}'
    page = 1
    has_more_pages = True
    fewer_than_10k_results = True

    while has_more_pages and fewer_than_10k_results:
    #while page == 1:
        # set page value and request page from OpenAlex
        url = works_query_with_page.format(page)
        page_with_results = requests.get(url).json()
            
        # loop through page of results
        results = page_with_results['results']
        for i, work in enumerate(results):
            title = work['display_name']
            if valid_title(title):
                parse_work(work, data)
            
        page += 1
            
        # end loop when either there are no more results on the requested page 
        # or the next request would exceed 10,000 results
        page_size = page_with_results['meta']['per_page']
        has_more_pages = len(results) == page_size
        fewer_than_10k_results = page_size * page <= 10000

def process_data(data):
    """
        :param data: Data object
    """
    for title in data.titles:
        if title != "Front Matter" and\
            title != "Back Matter" and\
            title != "Front Cover" and\
            title != "Back Cover":
            pass
    #print(data.institutions)
    dict = {'author' : data.authors, 'title' : data.titles, 'year' : data.years}
    #print(dict)
    df = pd.DataFrame(dict)
    print(df.head())
    df.to_csv("../data.csv")
    map_points([], '')

if __name__ == "__main__":
    gesta_id = "S21591069"
    main(gesta_id)
 