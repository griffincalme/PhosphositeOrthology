import pandas as pd
from sqlalchemy import create_engine



def merge_oma_dbPAF():
    engine = create_engine('sqlite:///phosphosite_orthology.db')  # create db in outside directory
    engine_out = create_engine('sqlite:///phosphosite_orthology_merged.db')  # create db in outside directory


    table_iter = engine.execute("SELECT name FROM sqlite_master WHERE type='table';")


    table_list = [i[0] for i in table_iter]
    identifier_set = {i[:5] for i in table_list}
    dbPAF__table_list = [i for i in table_list if 'dbPAF' in i]
    uniprot_table_list = [i for i in table_list if 'UniprotIDs' in i]


    join_table_triplets = []
    for i in uniprot_table_list:
        temp_list = [i]
        for j in dbPAF__table_list:
            if j[:5] in i:
                temp_list.append(j)
        join_table_triplets.append(temp_list)

    #print(join_table_triplets)

    for i in join_table_triplets:
        #print(i)
        df_uniprot = pd.read_sql_table(i[0], con=engine)
        df_1 = pd.read_sql_table(i[1], con=engine)
        df_2 = pd.read_sql_table(i[2], con=engine)

        species_id_1 = i[1][:5]  #e.g. CAEEL
        species_id_2 = i[2][:5]  #e.g. HUMAN

        # the join is species-naiive as long as uniprotID comes first in list
        # this can work if human and other organism swap places in list, due to ID (CAEEL) slicing above
        # which uses the same list index
        df_intermediate = pd.merge(df_uniprot, df_1, how='left', on=species_id_1)
        df_final = pd.merge(df_intermediate, df_2, how='left', on=species_id_2)

        # delete rows with missing sequences
        sequence_cols = [col for col in df_final.columns if 'Sequence' in col]
        df_final = df_final.dropna(subset=sequence_cols)

        df_final.to_sql(i[0], engine_out, index=False, if_exists='replace', chunksize=10000)


if __name__ == '__main__':
    merge_oma_dbPAF()


#df = pd.read_sql_table('CAEEL-HUMAN_UniprotIDs', con=engine)
#print(df.head())

# would be better to make SQL join rather than pandas ¯\_(ツ)_/¯
#join_intermediate = engine.execute("SELECT name FROM " + CAEEL_test_list[0] +
#                                   " LEFT JOIN " + CAEEL_test_list[0] + " ON " +
#                                   CAEEL_test_list[1] + ".CAEEL = " + CAEEL_test_list[0] + ".CAEEL")

#join_intermediate_df = pd.read_sql_table(join_intermediate, con=engine)
#print(join_intermediate_df.head())
#CAEEL_test_list = join_table_triplets[0]

#print('')
#------
#df_uniprot = pd.read_sql_table(CAEEL_test_list[0], con=engine)
#df_CAEEL = pd.read_sql_table(CAEEL_test_list[1], con=engine)
#df_HUMAN = pd.read_sql_table(CAEEL_test_list[2], con=engine)

#df_intermediate = pd.merge(df_uniprot, df_CAEEL, how='left', on='CAEEL')
#df = pd.merge(df_intermediate, df_HUMAN, how='left', on='HUMAN')

#print(df.head())

#df.to_excel('out3.xlsx', index=False)


