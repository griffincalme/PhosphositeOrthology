import pandas as pd
from sqlalchemy import create_engine
import os

def dbPAF_txt_to_db():
    engine = create_engine('sqlite:///phosphosite_orthology.db')  # create db in outside directory


    # for each dbPAF txt file, create a new table, probably could skip the step of converting elm to txt
    # just go from elm to individual dfs and then df to table (combine this script and extract_species_from_dbPAF script
    for dbPAF in os.listdir('extract_species_from_dbPAF/'):

        if dbPAF.endswith('dbPAF.txt'):
            #print('\n' + dbPAF)
            df = pd.read_table('extract_species_from_dbPAF/' + dbPAF)

            df = df.drop('dbPAF ID', 1)
            df = df.drop('PMIDs', 1)

            dbPAF = dbPAF[:-4]  # remove .txt

            # convert long-form to 5-letter abbreviation
            if dbPAF.startswith('Homo_sapiens'):
                abbrev_name = 'HUMAN_dbPAF'
            elif dbPAF.startswith('Mus_musculus'):
                abbrev_name = 'MOUSE_dbPAF'
            elif dbPAF.startswith('Saccharomyces_cerevisiae'):
                abbrev_name = 'YEAST_dbPAF'

            # takes first 3 genus letters, first 2 species letters, in uppercase
            else:
                split_list = dbPAF.split('_')

                abbrev_name = split_list[0][:3].upper() + split_list[1][:2].upper() + '_dbPAF'

            # rename cols with _HUMAN, _CAEEL, etc
            df.columns = [str(col) + '_' + abbrev_name[:-6] for col in df.columns]

            # rename Uniprot to HUMAN, CAEEL, etc
            df = df.rename(columns={'Uniprot_' + abbrev_name[:-6]: abbrev_name[:-6]})

            #print(abbrev_name[:-6])

            df.to_sql(abbrev_name, engine, index=False, if_exists='replace', chunksize=10000)


if __name__ == '__main__':
    dbPAF_txt_to_db()