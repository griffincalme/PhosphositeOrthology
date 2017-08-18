import os
import pandas as pd
import ast


def expand_ortholog_uniprot_id():
    orthologs_output_dir = 'uniprot_PairwiseOrthologs/'

    for ortho_filename in os.listdir(orthologs_output_dir):
        #print(orthologs_output_dir + ortho_filename)

        df = pd.read_table(orthologs_output_dir + ortho_filename)
        #print(df.head())

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

        # overwrite original file with expanded file
        df_out.to_csv(orthologs_output_dir + ortho_filename, sep='\t', index=False)


if __name__ == '__main__':
    expand_ortholog_uniprot_id()
