# requires oma-uniprot.txt

import pandas as pd
import time
import os
from collections import defaultdict
import ast


start_secs = time.time()


def make_dir(path):
    try:
        os.makedirs(path)
    except:
        pass


def remove_header_lines(file_in, file_out, junk_string):
    with open(file_in) as oldfile, open(file_out, 'w') as newfile:
        for line in oldfile:
            if junk_string not in line:
                newfile.write(line)



def pairwise_to_uniprot():
    uniprot_conversion_table = 'oma-uniprot.txt'
    conversion_table_clean = 'oma-uniprot_clean.txt'  # remove junk header lines


    # remove header lines from oma to uniprot conversion table
    remove_header_lines(uniprot_conversion_table, conversion_table_clean, '#')

    # import oma-uniprot conversion table
    conversion_df = pd.read_table(conversion_table_clean, names=['OMA_ID', 'uniprot_ID'])

    #print('\nConversion table\n')
    #print(conversion_df.head())

    # keep only rows without underscore in uniprotID (e.g. 'CDON_HUMAN'), dbPAF does not use this type of UniProt ID anyways
    conversion_df = conversion_df[conversion_df.uniprot_ID.str.contains('_') == False]

    ########

    # old dict method overwrites values for duplicate keys
    # conversion_dict = list(conversion_df.set_index('OMA_ID').to_dict().values()).pop()

    # new method, although slower, preserves all values inside lists
    # it works!
    # print(def_dict['HUMAN20719']) returns ['P35222', 'A0A024R2Q3'] don't forget underscored items were cleaned out

    # make intermediate list groupings of analogous IDs
    # {"HUMAN02..." : ['A0A0...', 'Q9H6...', etc...]
    # replace OMA id in main df cell with uniprot list


    # need default dict object to append values of identical keys to growing value lists
    def_dict = defaultdict(list)

    for index, row in conversion_df.iterrows():
        oma_id = row['OMA_ID']
        uniprot_id = row['uniprot_ID']
        def_dict[oma_id].append(uniprot_id)

    # default dict to regular dict
    conversion_dict = dict(def_dict)


    ########


    #print('\n\nConversion dictionary built, running ID translation...\n')
    #print('\n')

    orthologs_output_dir = 'uniprot_PairwiseOrthologs/'
    make_dir(orthologs_output_dir)

    orthologs_input_dir = 'OMAPairwiseOrthologs/'

    for ortho_filename in os.listdir(orthologs_input_dir):
        #print(orthologs_input_dir + ortho_filename)

        formatted_ortholog = orthologs_output_dir + ortho_filename

        # remove junk header lines
        remove_header_lines((orthologs_input_dir + ortho_filename), formatted_ortholog, '#')

        df = pd.read_table(formatted_ortholog,
                           names=['protein1', 'protein2', 'organism1', 'organism2', 'orthology_type', 'oma_group'])

        df['organism1'] = [i.split(' |')[0] for i in df['organism1']]  # keep only OMA identifier
        df['organism2'] = [i.split(' |')[0] for i in df['organism2']]

        new_name1 = df['organism1'][0][:5]
        new_name2 = df['organism2'][0][:5]  # new col name is 5-letter initial e.g. 'HUMAN', 'MOUSE, 'CAEEL'

        df.columns = df.columns.str.replace('organism1', new_name1)
        df.columns = df.columns.str.replace('organism2', new_name2)

        # Translate organism OMA ID to UniProt ID in df using conversion dict
        df[new_name1].update(df[new_name1].map(conversion_dict))

        # Translate human OMA ID to UniProt ID
        df[new_name2].update(df[new_name2].map(conversion_dict))

        ########
        # Make new row in df for each possible ID translation in conversion_df
        # so "HUMAN02..."  --> A0A0....
        #                  --> Q9H6....
        #                  --> etc... up to 8 uniprot ID translations per OMA
        # expand lists of uniprot IDs into own rows
        ########
        '''
        df_expanded = pd.DataFrame()
        for indexA, rowA in df.iterrows():
            animal_index = 2
            row_2_str = rowA[animal_index]  # CAEEL row, etc
    
            if row_2_str[:5] == df.columns.values.tolist()[animal_index]:  # if column header 'CAEEL' matches row cell
                df_expanded = df_expanded.append(rowA)                     # then don't interpret as list
    
            else:
                literal_row_2 = ast.literal_eval(row_2_str)  # interprets ['blah', 'foo', 'bar'] as list rather than string
                for i in literal_row_2:                      # for each element in cell list, make new row
                    temp_rowA = rowA                         # make temporary copy to overwrite, need to preserve
                    temp_rowA[animal_index] = i              # overwrite animal column with individual uniprot id
    
                    df_expanded = df_expanded.append(temp_rowA)      # save new row
    
    
        df_out = pd.DataFrame()
        for indexB, rowB in df_expanded.iterrows():
            human_index = 'HUMAN'
            row_3_str = rowB[human_index]  # HUMAN row
    
            if row_3_str[:5] == 'HUMAN':              # maybe should do try/except rather than hard code if/else to detect
                df_out = df_out.append(rowB)          # leftover OMA IDs that are true strings not lists
    
            else:
                literal_row_3 = ast.literal_eval(row_3_str)  # interprets ['blah'] as a list rather than a string, [3]rd col
                for i in literal_row_3:                      # for each element in cell list, make new row
                    temp_rowB = rowB                         # make temporary copy to overwrite, need to preserve
                    temp_rowB[human_index] = i               # overwrite animal column with individual uniprot id
    
                    df_out = df_out.append(temp_rowB)        # save new row
    
        ########
    
        #df_out.to_csv(orthologs_output_dir + ortho_filename[:-4] + '_UniprotIDs.txt', sep='\t', index=False)
        '''
        df.to_csv(orthologs_output_dir + ortho_filename[:-4] + '_UniprotIDs.txt', sep='\t', index=False)

        # delete temporary 'cleaned pairwise ortholog' files
        os.remove(formatted_ortholog)


    # delete temporary 'cleaned oma-uniprot conversion' file
    os.remove(conversion_table_clean)

if __name__ == '__main__':
    pairwise_to_uniprot()



#end_secs = time.time()
#runsecs = end_secs - start_secs
#print(' ')
#print(str(round(runsecs, 2)) + ' seconds')


