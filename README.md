# Work in progress: Diversity in Gesta

Gesta is a leading peer-reviewed academic journal in the area of medieval art.

Target functionality: Generate visualizations of trends in gender and region of origin of Gesta-published authors.

Current functionality: Maps locations of institutions with which Gesta-published authors are affiliated.

*Note:* Script can easily be generalized to other journals via commandline; Gesta is the motivating example and set as default. 

### Use Instructions

After cloning, add the following function which returns your email address to `mailto.py`. This will be a commandline argument later. 

This is the address used as the reply-to for OpenAlex API calls.  

    def email():
        return your_address@gmail.com

In terminal and from directory `gesta-diversity`:

0. For first time set-up, build the conda environment which will allow access to all necessary packages:
<!--- Make code --->
     conda env create -f journal-diversity.yml

1. Activate the environment:
<!--- Make code --->
    conda activate journal-diversity

2. Run the program:
### usage in terminal:
<!--- Make code --->
    python diversity.py email [-h] [-v] [-n JOURNAL_NAME] [-i ID] [-c] [-m] [--start_year START_YEAR] [--end_year END_YEAR] 

### positional arguments:
  email                 the reply-to email for OpenAlex API calls

#### options:

  -h, --help            show this help message and exit

  -v, --verbose         include to print progress messages

  -n --journal_name JOURNAL_NAME
                        name of journal or source to search for

  -i --journal_id ID
                        OpenAlex id of journal to analyze - defaults to Gesta if unspecified

  -c, --write_csv       include to write csv of data

  -m, --write_maps      include to plot locations of affiliated institutions

  --start_year START_YEAR 
                        filter publications by this earliest year (inclusive)

  --end_year END_YEAR   filter publications by this latest year (inclusive)


Thank you to OpenAlex:

    Priem, J., Piwowar, H., & Orr, R. (2022). OpenAlex: A fully-open index of scholarly works, authors, venues, institutions, and concepts. ArXiv. https://arxiv.org/abs/2205.01833

## To-Do

-  make protocol for what fields to query to get locations?
    ie get institution ID, else get institution name and country, else get author name and country and year?
- look into Genderize API to get gender stats
- look into reconstructing abstracts from one-hot encoding
- swap print statements for progress bar


<!--- NOTES --->
<!---- issn_l = "0016-920X" --->
<!---- source_query = "https://api.openalex.org/sources/" + args.id --->