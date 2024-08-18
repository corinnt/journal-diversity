# Diversity in Academic Publications

Generate visualizations of trends in gender and region of origin of scholars published in a given academic journal, as well as summary statistics and a CSV of data for further analysis.

This tool can be used to analyze any journal in the OpenAlex database. [OpenAlex](https://help.openalex.org/) is a free and open catalog of the global research system. Analyzing Gesta, a leading peer-reviewed academic journal in the area of medieval art, was the motivating example for this tool. 

*example: generate maps of institutional affiliations of authors (Gesta, 2010-2020)*
    
    python main.py -m --start_year 2010 --end_year 2020 --verbose

![alt text](README_imgs/gesta-map.png?raw=true) 


*example: generate plots of gender of authors over time (USENIX, random sample of 500 papers)*

    python main.py -n usenix -s 500 -g --verbose

![alt text](README_imgs/sampled-usenix-gender.png?raw=true) 

## Use Instructions


### 0. For first time set-up:
Set up your `config` file with an email to use as the reply-to for API calls, as well as filepaths to route data to. In order to use the gender analysis features, you will need to make an account with [Namsor](https://namsor.app/) to get an API key.

Build the conda environment to access the necessary packages:
<!--- Make code --->
     conda env create -f journal-diversity.yml

### 1. Activate the environment:
<!--- Make code --->
    conda activate journal-diversity

### 2. Run the program:

#### use in terminal:
<!--- Make code --->
    main.py [-h] [-s SAMPLE_SIZE] [-v] [-a] [-g] [-m] [-r] [--start_year START_YEAR] [--end_year END_YEAR]
               config_path journal_name
#### positional arguments: 
  `config_path`               path to the config file
  
  `journal_name`              name of journal or source to search for

#### options:

  `-h`, `--help`                show this help message and exit

  `-r`, `--restore_saved`       include to restore saved data

  `-s SAMPLE_SIZE`, `--sample SAMPLE_SIZE`
                                include sample size (max of 10,000) to analyze subset

  `-v`, `--verbose`             include to print progress messages

  `-a`, `--write_abstracts`     include to write abstracts of all works to csv

  `-g`, `--predict_gender`      include to predict genders of all authors and write to csv

  `-m`, `--write_maps `         include to plot locations of affiliated institutions

  `--start_year START_YEAR`     filter publication dates by this earliest year (inclusive)

  `--end_year END_YEAR`         filter publication dates by this latest year (inclusive)

### Note on gender prediction
This tool uses Namsor, which classifies personal names into binary male/female categories. This serves as an estimate, as gender is not binary and the software is not 100% accurate.

## Sources:

OpenAlex:

    Priem, J., Piwowar, H., & Orr, R. (2022). OpenAlex: A fully-open index of scholarly works, authors, venues, institutions, and concepts. ArXiv. https://arxiv.org/abs/2205.01833

PyGMT:

    Wessel, P., Luis, J. F., Uieda, L., Scharroo, R., Wobbe, F., Smith, W. H. F., & Tian, D. (2019). The Generic Mapping Tools version 6. Geochemistry, Geophysics, Geosystems, 20, 5556– 5564. https://doi.org/10.1029/2019GC008515