# input list of human uniprot identifiers, returns matrix describing which animals have orthologous site

import pandas as pd
import os


df = pd.read_csv('mylist.csv')

# check in resulting griffin orthologs, after phosphosite alignment matching
for csv in os.listdir('aligned_phos_ortholog_pairs'):
    ortholog_df = pd.read_csv('aligned_phos_ortholog_pairs/' + csv)
    organism_name = csv[:5]

    df[organism_name + ' orthologous phosphosite'] = df['my_human_uniprot_id'].isin(ortholog_df['HUMAN']) & \
                                                     df['Position'].isin(ortholog_df['Position_HUMAN']) & \
                                                     df['Type'].isin(ortholog_df['Type_HUMAN'])


df.to_csv('checkmylist_results.csv', index=False)