import requests

class Counts():
    def __init__(self):
        self.titles = []
        self.countries = {}
        self.institutions = {}

def main(source_id):
    issn_l = "0016-920X"
    source_query = "https://api.openalex.org/sources/" + source_id
    counts = Counts()
    populate_work_dictionaries(source_id, counts)
    # url with a placeholder for page number
    #works_query_with_page = 'https://api.openalex.org/works?filter=locations.source.id:' + gesta_id + '&page={}'
    #print(work_IDs)
    for title in counts.titles:
        if title != "Front Matter" and\
            title != "Back Matter" and\
            title != "Front Cover" and\
            title != "Back Cover":
            pass
    print(counts.institutions)
    # TODO: make protocol for what fields to query?
    # ie get institution ID, else get institution name and country, else get author name and country and year?

def increment(key, dict):
    if key in dict:
        dict[key] += 1
    else:
        dict[key] = 1

def populate_authorship(authorships, counts):
    """
        :param authorships: list of authorship objects from the OpenAlex API
        :param country_counts: dictionary mapping country codes to instance count
        :param institution_counts: dictionary mapping OpenAlex institution IDs to counts of their occurrences
    """
    #print("#authorships: " + str(len(authorships)))
    for authorship in authorships:
        #print("#institutions: " + str(len(authorship['institutions'])))
        for institution in authorship['institutions']:
            code = institution['country_code']
            id = institution['id']
            increment(code, counts.countries)
            increment(id, counts.institutions)

def populate_work_dictionaries(source_id, counts):
    """
    :param source_id: string - OpenAlex ID of the source to analyze
    :param counts: Counts object
    """
    # only get name and authors for after 1999
    works_query_with_page = 'https://api.openalex.org/works?select=display_name,authorships&filter=publication_year:>1999,locations.source.id:' + source_id + '&page={}'
    
    # get all Work info after 1999
    #works_query_with_page = 'https://api.openalex.org/works?select=display_name,authorships&page={}'
    page = 1
    has_more_pages = True
    fewer_than_10k_results = True
    # loop through pages        
    while has_more_pages and fewer_than_10k_results:
    #while page == 1:  
        # set page value and request page from OpenAlex
        url = works_query_with_page.format(page)
        print('\n' + url)
        page_with_results = requests.get(url).json()
            
        # loop through page of results
        results = page_with_results['results']
        for i, work in enumerate(results):
            title = work['display_name']
            counts.titles.append(title)
            if title:
                print(title)
            else:
                print("MISSING TITLE")
            authorship_list = work['authorships']
            if authorship_list:
                print(str(authorship_list) + "\n\n")
                populate_authorship(authorship_list, counts)
            else:
                print("MISSING AUTHORSHIPS\n\n")
            #print(openalex_id, end='\t' if (i+1)%5!=0 else '\n')
            # next page
        page += 1
            
        # end loop when either there are no more results on the requested page 
        # or the next request would exceed 10,000 results
        page_size = page_with_results['meta']['per_page']
        has_more_pages = len(results) == page_size
        fewer_than_10k_results = page_size * page <= 10000

if __name__ == "__main__":
    gesta_id = "S21591069"
    main(gesta_id)
 