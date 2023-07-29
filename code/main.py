import sys
import argparse
import util
from dataclass import Data

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

def main(args):
    
    data = Data(args)

    if args.journal_name:
        data.set_journal(args.journal_name)
    else:
        data.id = 'S21591069' # Default Gesta
        data.num_works = 1091

    if args.restore_saved:
        data = util.unpickle_data('../data/pickled_data')
        data.display_data()    
    else:
        institution_ids, author_ids = data.iterate_search(args)
        data.add_all_geodata(institution_ids, author_ids)
        #analyze_data(data)
        data.display_data()    
        util.pickle_data(data)


if __name__ == "__main__":
    args = parseArguments()
    main(args)