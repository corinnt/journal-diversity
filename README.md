# Work in progress: Diversity in Gesta

*Gesta is a leading peer-reviewed academic journal in the area of medieval art.*

Maps locations of institutions affiliated with authors of articles published in Gesta. 

### Use Instructions

After cloning, add the following function which returns your email address to `mailto.py`. 

This is the address used as the reply-to for OpenAlex API calls.  

    def email():
        return your_address@gmail.com

In terminal and from directory `gesta-diversity`:

0. For first time set-up, build the conda environment which will allow access to all necessary packages:

     `conda env create -f journal-diversity.yml`

1. Activate the environment:

    conda activate journal-diversity

2. Run the program:
    
    `sh diversity.sh`


Thank you to OpenAlex:

    Priem, J., Piwowar, H., & Orr, R. (2022). OpenAlex: A fully-open index of scholarly works, authors, venues, institutions, and concepts. ArXiv. https://arxiv.org/abs/2205.01833