# Griffin Calme 2017, Python 3
# This script takes the dbPAF TOTAL.elm and copies only the 7 desired species into SQLite db

import pandas as pd
from sqlalchemy import create_engine
import os

def extract_species_from_dbPAF():

    engine = create_engine('sqlite:///phosphosite_orthology.db')  # create db in outside directory
    dbPAF = 'TOTAL.elm'
    extract_dir = 'extract_species_from_dbPAF/'

    paf_df = pd.read_table(dbPAF)


    # Get unique species names
    species_list = []
    for row in paf_df['Species']:
        if row in species_list:
            pass
        else:
            species_list.append(row)

    #print(species_list)

    if not os.path.exists(extract_dir):
        os.makedirs(extract_dir)

    # for each unique species name, filter and save species as separate file
    # basically an excel filter
    for i in species_list:
        #print(i)
        new_df = paf_df[paf_df["Species"] == i]  # create new dataframe for each species in TOTAL.elm
        i_list = i.split('(', 1)  # Truncate name
        i = i_list[0]  # only take parts of name before parentheses
        i = i.rstrip()  # remove trailing whitespaces
        i = i.replace(" ", "_")  # replace space with underscore

        #new_df.to_excel(i + '.xlsx', sheet_name='Sheet1', index=False) # excel filetype is compressed but slower
        #new_df.to_csv(extract_dir + i + '_dbPAF.txt', sep='\t', index=False)


    # To do it individually, uncomment these and comment out the for loop directly above
    #i = 'Saccharomyces cerevisiae (strain ATCC 204508 / S288c)(Baker\'s yeast)'
    #new_df = paf_df[paf_df["Species"] == i]
    #new_df.to_excel('Saccharomyces cerevisiae' + '.xlsx', sheet_name='Sheet1', index=False)


if __name__ == '__main__':
    extract_species_from_dbPAF()