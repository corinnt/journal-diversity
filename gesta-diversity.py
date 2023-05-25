import requests

def main():
    issn_l = "0016-920X"
    gesta_id = "S21591069"
    source_query = "https://api.openalex.org/sources/" + gesta_id
    work_IDs, titles = populate_work_dictionaries(gesta_id)
    # url with a placeholder for page number
    #works_query_with_page = 'https://api.openalex.org/works?filter=locations.source.id:' + gesta_id + '&page={}'
    #print(work_IDs)
    for title in titles:
        if title != "Front Matter" and title != "Back Matter" and title != "Front Cover":
            print(title + "\n")
    #print(titles)


def populate_work_dictionaries(gesta_id):
    """
    :param gesta_ID: 
    
    """
    works_query_with_page = 'https://api.openalex.org/works?filter=publication_year:>1999,locations.source.id:' + gesta_id + '&page={}'

    page = 1
    has_more_pages = True
    fewer_than_10k_results = True

    work_IDs = []
    titles = []
    # loop through pages        
    while has_more_pages and fewer_than_10k_results:
        
        # set page value and request page from OpenAlex
        url = works_query_with_page.format(page)
        print('\n' + url)
        page_with_results = requests.get(url).json()
            
            # loop through partial list of results
        results = page_with_results['results']
        for i, work in enumerate(results):
            openalex_id = work['id'].replace("https://openalex.org/", "")
            title = work['display_name']
            work_IDs.append(openalex_id)
            titles.append(title)
            print(openalex_id, end='\t' if (i+1)%5!=0 else '\n')

            # next page
        page += 1
            
            # end loop when either there are no more results on the requested page 
            # or the next request would exceed 10,000 results
        per_page = page_with_results['meta']['per_page']
        has_more_pages = len(results) == per_page
        fewer_than_10k_results = per_page * page <= 10000
    return work_IDs, titles

if __name__ == "__main__":
    main()
