import pandas as pd
from sqlalchemy import create_engine
import os

def pairwise_to_db():
    engine = create_engine('sqlite:///phosphosite_orthology.db')  # create db in outside directory


    # for each dbPAF txt file, create a new table, probably could skip the step of converting elm to txt
    # just go from elm to individual dfs and then df to table (combine this script and extract_species_from_dbPAF script

    directory = 'uniprot_PairwiseOrthologs/'

    for ortholog_file in os.listdir(directory):
        if ortholog_file.endswith('UniprotIDs.txt'):
            #print('\n' + ortholog_file)
            df = pd.read_table(directory + ortholog_file)

            df = df.drop('protein1', 1)
            df = df.drop('protein2', 1)
            #print(df.head())

            df.to_sql(ortholog_file[:-4], engine, index=False, if_exists='replace', chunksize=10000)

if __name__ == '__main__':
    pairwise_to_db()