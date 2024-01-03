# Work in progress: Diversity in Academic Publications

Generate visualizations of trends in gender and region of origin of scholars published in a given academic journal.

Note: Script can be used to analyze any journal found in the OpenAlex database; Gesta, a leading peer-reviewed academic journal in the area of medieval art, is set as the default. 

*example to generate maps of publications in Gesta starting in 1999:*
    
    python main.py -v -m --start_year 1999

## Use Instructions

In terminal and from directory `gesta-diversity`

### 0. For first time set-up:

    Set up your `config` file with an email to use as the reply-to for API calls, as well as filepaths to route data to. In order to use the gender analysis features, you will need to make an account with (Namsor)[https://namsor.app/] to get an API key.

    Build the conda environment to access the necessary packages:
<!--- Make code --->
     conda env create -f journal-diversity.yml

### 1. Activate the environment:
<!--- Make code --->
    conda activate journal-diversity

### 2. Run the program:

#### use in terminal:
<!--- Make code --->
    main.py config_path [-h] [-n JOURNAL_NAME] [-v] [-a] [-g] [-m] [-r] [--start_year START_YEAR] [--end_year END_YEAR] 
#### positional arguments:f
  `config_path`             the path to your config file

#### options:

  `-h`, `--help`            show this help message and exit
  
  `-n`, `--name`            include to specify a journal name for which to search

  `-v`, `--verbose`         include to print progress messages

  `-m`, `--write_maps`      include to plot locations of affiliated institutions

  `-g`, `--predict_genders` include to predict + plot genders of authors with Namsor API

  `r`, `--restore`          

  `--start_year START_YEAR` 
                            filter publications by this earliest year (inclusive)

  `--end_year END_YEAR`     filter publications by this latest year (inclusive)

  `-n JOURNAL_NAME`, `--journal_name JOURNAL_NAME`
                            name of journal or source to search for

Snippet of map of Gesta publications from 2010-2020:

![alt text](readme_map.png?raw=true)

Graph of gender over time in Gesta publications from 2000-2020:

![alt text](gender-over-time.png?raw=true)

## Sources:

OpenAlex:

    Priem, J., Piwowar, H., & Orr, R. (2022). OpenAlex: A fully-open index of scholarly works, authors, venues, institutions, and concepts. ArXiv. https://arxiv.org/abs/2205.01833

PyGMT:

    Wessel, P., Luis, J. F., Uieda, L., Scharroo, R., Wobbe, F., Smith, W. H. F., & Tian, D. (2019). The Generic Mapping Tools version 6. Geochemistry, Geophysics, Geosystems, 20, 5556– 5564. https://doi.org/10.1029/2019GC008515

## To-Do

- fix error handling for OpenAlex request limiting
- make GeoData class
- add Namsor citation