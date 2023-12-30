import sys
import argparse
import util
from dataclass import Data
from gender import predict_gender

def parseArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("email", help="the reply-to email for OpenAlex API calls") # required=True,
    parser.add_argument("-v", "--verbose", action="store_true", help="include to print progress messages")

    parser.add_argument("-n", "--journal_name", dest="journal_name", 
        type=str, default=None, help="name of journal or source to search for")

    parser.add_argument("-c", "--write_csv", dest="csv", 
        action="store_true", help="include to write csv of data") 

    parser.add_argument("-a", "--write_abstracts", dest="abstracts", 
        action="store_true", help="include to write abstracts of all works to csv") 

    parser.add_argument("-g", "--predict_gender", dest="gender", 
        action="store_true", help="include to predict genders of all authors and write to csv") 

    parser.add_argument("-m", "--write_maps", dest="maps", 
        action="store_true", help="include to plot locations of affiliated institutions") 

    parser.add_argument("-r", "--restore_saved", action="store_true", help="include to restore saved data") 
    parser.add_argument("--start_year", dest="start_year", type=int, default=None, help="filter publication dates by this earliest year (inclusive)")
    parser.add_argument("--end_year", dest="end_year", type=int, default=None, help="filter publication dates by this latest year (inclusive)")

    args = parser.parse_args()
    if args.verbose: 
        util.VERBOSE = True
    return args

def get_journal(args):
        """ Returns the OpenAlex Work ID of the top result matching the input journal name
        :param args: parsed user argument object
        :returns str, int: ID of journal, count of Works in source
        """    
        url = "https://api.openalex.org/sources?search=" + args.journal_name + '&mailto=' + args.email
        results = util.api_request(url)
        if not results: print("No results for journal.") # TODO - test that results would be None if len(results) == 0? 
        top_result = results['results'][0]
        if 'id' in top_result: 
            util.info("got id of " + top_result['display_name']) # POSSBUG: multiple journals of same name
            id = top_result['id']
            #num_works = top_result['works_count']
            return id#, num_works
        else: 
            raise Exception("No results found for journal " + args.journal_name + " in OpenAlex database.")

def main(args):
    data = Data(args)
    if args.journal_name:
        source_id = get_journal(args.journal_name)
    else:
        source_id = 'S21591069' # Default Gesta
        #data.num_works = 1091
   
    if args.restore_saved:
        util.info("Restoring saved data from ../data/pickled_data.csv")
        data = util.unpickle_data('../data/pickled_data')
        if data.source_id != source_id:
            raise Exception("Searched source ID does not match saved source ID.")
    else:
        data.source_id = source_id
        institution_ids, author_ids = data.iterate_search(args)
        print('THROUGH ITERATE SEARCH')
        data.add_geodata(institution_ids, author_ids) 
        data.add_genders()

    data.display_data()    
    util.pickle_data(data)

if __name__ == "__main__":
    args = parseArguments()
    main(args)

