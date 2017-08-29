# this program breaks down into a csv where phosphosite orthologs could be lost in the PhosphositeOrthology program
# PhosphositePlus is being used to verify that my orthologs are correct but PSP does not have everything which is the
# reason for using dbPAF
# we want to make sure that the UniprotIDs contained in BOTH PSP and dbPAF end up in the orthologs list (ID_in_dbPAF)
# possible reasons why the candidates may not make it through are:

# dbPAF-OMA conversion table does not contain uniprotID -- see about checking both rev & unrev ID (ID_in_dbPAF_OMA_conversion_table)
# **** issues with having both reviewed and unreviewed ids in conversion table
# OMA program does not actually identify ortholog that PSP does -- in this case no fix (in_OMA_orthologs)
# or my alignment does not work well to identify phos orthologs (in_griffin_phos_orthologs)

import pandas as pd
from sqlalchemy import create_engine
import os

# Don't use excel file, interprets genes as dates
dbPAF_df = pd.read_table('../TOTAL.elm', dtype=object)
psp_df = pd.read_table('Phosphorylation_site_dataset.tab', dtype=object)

psp_df = psp_df.loc[psp_df['ORGANISM'].isin(['human', 'mouse', 'rat', 'fruit fly'])]  # filter out animals not in this list

comparison_df = psp_df[['SITE_GRP_ID', 'ORGANISM', 'ACC_ID', 'PROTEIN', 'MOD_RSD']].copy()  # copy only necessary columns
comparison_df.rename(columns={'SITE_GRP_ID': 'PSP_SITE_GRP_ID', 'ACC_ID': 'Uniprot_ACC_ID'}, inplace=True)  # give cols more specific names


comparison_df['Position'] = comparison_df.MOD_RSD.str[1:-2]  # 'S23-p'  --> '23'    # Position is also str in dbPAF_df
comparison_df['Type'] = comparison_df.MOD_RSD.str[0]  # 'S23-p'  --> 'S'


# check if the UniprotIDs in PhosphositePlus are also in dbPAF
comparison_df['ID_in_dbPAF'] = comparison_df['Uniprot_ACC_ID'].isin(dbPAF_df['Uniprot'])

# check if UniprotID, site, and amino acid type from PSP are also in dbPAF
comparison_df['ID_and_site_in_dbPAF'] = comparison_df['Uniprot_ACC_ID'].isin(dbPAF_df['Uniprot']) \
                                        & comparison_df['Position'].isin(dbPAF_df['Position']) \
                                        & comparison_df['Type'].isin(dbPAF_df['Type'])

# check if the UniprotIDs from PSP are in the dbPAF to OMA conversion table
oma_uniprot_df = pd.read_table('oma-uniprot_clean.txt', dtype=object)
comparison_df['ID_in_OMA-dbPAF_conversion_table'] = comparison_df['Uniprot_ACC_ID'].isin(oma_uniprot_df['uniprot'])


# check if UniprotID in OMA orthologs file
engine = create_engine('sqlite:///../phosphosite_orthology.db')  # create db in outside directory
table_iter = engine.execute("SELECT name FROM sqlite_master WHERE type='table';")

ortholog_species_pairs = ['CAEEL-HUMAN_UniprotIDs', 'DROME-HUMAN_UniprotIDs', 'MOUSE-HUMAN_UniprotIDs',
                          'RATNO-HUMAN_UniprotIDs', 'SCHPO-HUMAN_UniprotIDs', 'YEAST-HUMAN_UniprotIDs']

oma_ortholog_df = pd.DataFrame()
for i in ortholog_species_pairs:
    temp_oma_orth_df = pd.read_sql_table(i, engine)
    temp_oma_orth_df = temp_oma_orth_df.rename(columns={i[:5]: 'species'})  # rename organism to facilitate appending
    oma_ortholog_df = oma_ortholog_df.append(temp_oma_orth_df)

oma_ortholog_df = oma_ortholog_df.drop(['oma_group', 'orthology_type'], axis=1)

comparison_df['ID_in_OMA_orthologs'] = comparison_df['Uniprot_ACC_ID'].isin(oma_ortholog_df['HUMAN']) \
                                        | comparison_df['Uniprot_ACC_ID'].isin(oma_ortholog_df['species'])


# check in resulting griffin orthologs, after phosphosite alignment matching
phos_ortholog_df = pd.DataFrame()
for csv in os.listdir('aligned_phos_ortholog_pairs'):
    temp_phos_ortholog_df = pd.read_csv('aligned_phos_ortholog_pairs/' + csv)
    temp_phos_ortholog_df = temp_phos_ortholog_df.rename(columns={csv[:5]: 'species'})
    phos_ortholog_df = phos_ortholog_df.append(temp_phos_ortholog_df)  # df of ortholog animal-human uniprot ID pairs


# darn, this doesn's account for the phosphosite, only the ID?????
# use | for bitwise or rather than boolean 'or' for pandas, checks all the comparison_df id's in both human and animal
#  columns of phos_orthology_df
comparison_df['ID_in_griffin_phos_orthologs'] = comparison_df['Uniprot_ACC_ID'].isin(phos_ortholog_df['HUMAN']) | \
                                             comparison_df['Uniprot_ACC_ID'].isin(phos_ortholog_df['species'])

# print(dbPAF_df.head())
print('\n')
print(comparison_df.head())
print('\n')
#print(phos_ortholog_df.head())


 # TRY TO FINISH THIS COLUMN TOO:
#phos_ortholog_df[0] = phos_ortholog_df[0] + phos_ortholog_df[2] + phos_ortholog_df[8]
#phos_ortholog_df[1] = phos_ortholog_df[1] + phos_ortholog_df[3] + phos_ortholog_df[9]

#phos_ortholog_df.to_csv('is_this_work.csv', index=False)
#comparison_df['ID_and_site_in_griffin_phos_orthologs'] = comparison_df['Uniprot_ACC_ID'].isin(phos_ortholog_df[0]) &\
#                                             comparison_df['Position'].isin(phos_ortholog_df[2]) &\
#                                             comparison_df['Type'].isin(phos_ortholog_df[8]) | \
#                                             comparison_df['Uniprot_ACC_ID'].isin(phos_ortholog_df[1]) & \
#                                             comparison_df['Position'].isin(phos_ortholog_df[3]) & \
#                                             comparison_df['Type'].isin(phos_ortholog_df[9])



comparison_df.to_csv('db_comparison_results.csv', index=False)




