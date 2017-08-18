import pandas as pd
from sqlalchemy import create_engine
from Bio import pairwise2
import time
import os

#start_secs = time.time()


def align_species_biopython():
    engine = create_engine('sqlite:///phosphosite_orthology_cleaned.db')  # create db in outside directory
    #engine_out = create_engine('sqlite:///phosphosite_orthologs_only_test_biopy.db')  # create db in outside directory
    if not os.path.exists('aligned_phos_ortholog_pairs/'):
        os.makedirs('aligned_phos_ortholog_pairs/')


    table_iter = engine.execute("SELECT name FROM sqlite_master WHERE type='table';")
    table_list = [i[0] for i in table_iter]

    # print(table_list)
    print('\n')

    # USE species_index TO CHANGE WHICH TABLE IS RUN, 0 = CAEEL, 1 = DROME, 2 = MOUSE ...
    for i in range(0,6):
        species_index = i
        species_id = table_list[species_index][:5]
        print(species_id + 'aln done...')
        new_aln_col_string = 'aln_' + species_id     # used to create a new df col 'aln_CAEEL' etc...

        # must change species ID (i.e. 'CAEEL') for each species sql table,
        # also change to appropriate table (i.e. table_list[0] is CAEEL)
        # don't forget to change the name of the saved CSV
        df = pd.read_sql_table(table_list[species_index], con=engine)

        species2_cols = [col for col in df.columns if str(species_id) in col] #list of all columns that contain identifier
        HUMAN_cols = [col for col in df.columns if 'HUMAN' in col]

        # print('')

        # accepts sequence and phosphosite position (1-based index), returns the position within the aln string(0-based index,
        # counts dashes of aligned seq)
        # 'F-RL--YWAD', 4 (pY4) --> 6
        def get_aln_phos_loc(seq, phosphosite_pos):
            letter_counter = 0
            character_counter = 0
            seq = str(seq)

            for j in seq:
                if j != '-':
                    if letter_counter == phosphosite_pos-1:
                        break
                    letter_counter += 1

                character_counter += 1
            return character_counter


        # checks if two sequences have the same letter at the same position
        # This requires sequences to be aligned (have hyphens inserted, and new string site position reindexed) to be accurate
        def check_homologous(aln_0, aln_1, phos_pos0, phos_pos1):

            # call aligned sequence indexer function
            aln_phosphosite0 = get_aln_phos_loc(aln_0, phos_pos0)
            aln_phosphosite1 = get_aln_phos_loc(aln_1, phos_pos1)
            #print(aln_phosphosite0)
            #print(aln_phosphosite1)
            if aln_phosphosite0 == aln_phosphosite1:
                #print('Match!!!')
                match_truth = True

            else:
                #print('No Match!')
                match_truth = False

            return match_truth


        last_seq_id_species2 = 'none'
        last_seq_id_HUMAN = 'none'

        homologous_df = pd.DataFrame()

        for index, row in df.iterrows():

            species2_list = [df[i][index] for i in species2_cols]  # df row to list for easier manipulation
            HUMAN_list = [df[i][index] for i in HUMAN_cols]

            species2_list[1] = int(species2_list[1])  # convert float type to int for phospho positions
            HUMAN_list[1] = int(HUMAN_list[1])

            # make phosphosite position 0-index rather than 1 (i.e. so 0th element is first letter, prevents off-by-1 error)
            species2_list[1] = species2_list[1] - 1
            HUMAN_list[1] = HUMAN_list[1] - 1

            # if the protein IDs are different from the last row, run new alignment
            if species2_list[0] != last_seq_id_species2 and HUMAN_list[0] != last_seq_id_HUMAN:
                alignments = pairwise2.align.globalxx(row[6], row['Sequence_HUMAN'])  # biopython align

                # is_match is True if aligned seqs match up same phosphosite position
                is_match = check_homologous(alignments[0][0], alignments[0][1], species2_list[1], HUMAN_list[1])
                if is_match is True:
                    homologous_df = homologous_df.append(df.iloc[[index]])
                    homologous_df.loc[index, 'aln_HUMAN'] = alignments[0][1]
                    homologous_df.loc[index, new_aln_col_string] = alignments[0][0]

            # reuse last alignment, save computation
            else:
                # is_match is True if aligned seqs match up same phosphosite position
                is_match = check_homologous(alignments[0][0], alignments[0][1], species2_list[1], HUMAN_list[1])
                if is_match is True:
                    homologous_df = homologous_df.append(df.iloc[[index]])
                    homologous_df.loc[index, 'aln_HUMAN'] = alignments[0][1]
                    homologous_df.loc[index, new_aln_col_string] = alignments[0][0]

            last_seq_id_species2 = species2_list[0]  # remember last protein ID to reuse same alignments
            last_seq_id_HUMAN = HUMAN_list[0]

            #print('index = ' + str(index))
            #print(alignments[0][0])
            #print(alignments[0][1])
            #print('\n')

        #print(homologous_df.head())

        # only rows with homologous phosphosites
        homologous_df.to_csv('aligned_phos_ortholog_pairs/' + table_list[species_index][:5] + '_align_phos_matches_BioPy.csv', index=False)

        #homologous_df.to_sql(table_list[0], engine_out, index=False, if_exists='replace', chunksize=10000)

if __name__ == '__main__':
    align_species_biopython()


#end_secs = time.time()
#runsecs = end_secs - start_secs
#print('\nTook ' + str(runsecs) + ' seconds')
