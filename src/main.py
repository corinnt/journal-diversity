import sys
import argparse
import util
from dataclass import Data
from gender import GenderData

def parseArguments():
    parser = argparse.ArgumentParser()
    #parser.add_argument("email", help="the reply-to email for OpenAlex API calls") # required=True,
    parser.add_argument("config_path", help="path to the config file")

    parser.add_argument("-n", "--journal_name", dest="journal_name", 
        type=str, default=None, help="name of journal or source to search for")

    parser.add_argument("-v", "--verbose", action="store_true", help="include to print progress messages")

    parser.add_argument("-a", "--write_abstracts", dest="abstracts", 
        action="store_true", help="include to write abstracts of all works to csv") 

    parser.add_argument("-g", "--predict_gender", dest="gender", 
        action="store_true", help="include to predict genders of all authors and write to csv") 

    parser.add_argument("-m", "--write_maps", dest="maps", 
        action="store_true", help="include to plot locations of affiliated institutions") 

    parser.add_argument("-r", "--restore_saved", action="store_true", help="include to restore saved data") 

    parser.add_argument("--start_year", dest="start_year", type=int, default=None, 
                        help="filter publication dates by this earliest year (inclusive)")
    
    parser.add_argument("--end_year", dest="end_year", type=int, default=None, 
                        help="filter publication dates by this latest year (inclusive)")

    args = parser.parse_args()
    if args.verbose: 
        util.VERBOSE = True
    return args

def main(args):
    config_json = util.load_config(args.config_path)
    if args.gender: 
        data = GenderData(args, config_json)
    else: 
        data = Data(args, config_json)

    if args.restore_saved:
        util.info("Restoring saved data.")
        cached_data = util.unpickle_data(data.config.data_src)
        if cached_data.source_id != data.source_id:
            raise Exception("Searched source ID does not match saved source ID. Check config file to confirm journal_data_src.")
        cached_data.display_data()
        return 
    util.info("Iterating through journal works...")
    institution_ids, author_ids = data.iterate_search()
    data.populate_additional_data(institution_ids, author_ids)
    data.display_data()
    util.pickle_data(data, dst=data.config.data_dst)
    util.info("Saved pickled data to " + data.config.data_dst + ".") 

if __name__ == "__main__":
    args = parseArguments()
    main(args)

