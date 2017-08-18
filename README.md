# Need to run through procedure again and polish readme, must be able to replicate
Must move non-functioning or deprecated scripts to `other` folder in order to better organize program

## requirements,
4GB RAM?
Python3
Non-Standard Packages: pandas, sqlalchemy, 
Standard: os, ast, collections, time, sqlite3
Linux to run OMA

## Step 1
Download dbPAF for all animal species
http://dbpaf.biocuckoo.org/download.php

If you download Total, use `extract_species_from_dbPAF.py` script to extract into individual species files

## Step 2 OMA ortholog search

Use OMA export to select all 7 organisms (human, mouse, rat, c. elegans, s. pombe, s. cerevisiae, d. melanogaster)
http://omabrowser.org/oma/export/

submit and wait to download oma export package, comes with linux/mac executables
navigate to OMA folder and run `./install.sh`
then run `bin/oma -n 4 parameters.drw`
change '4' to your number of cores or threads on the computer that you'd like to use.

wait a day for it to run
other orthology dbs to try: http://questfororthologs.org/orthology_databases


## Step 3 OMA output

You need to copy all of the pairwise orthologs of SPECIES-HUMAN.txt
there should be 6 txt files if you just ran the 7 species total (including human)
each of the 6 animals is paired with the human orthologs

Put these 6 text files in another folder titled PairwiseOrthologs in order to convert the OMA identifiers to UniProt identifiers. The UniProt identifier is needed to get phosphosite and protein sequence information from dbPAF.
Also download, unzip, and copy `oma-uniprot.txt`  http://omabrowser.org/All/oma-uniprot.txt.gz
This is the ID conversion table that will be used.

Run `pairwise_to_uniprot.py`
This creates tab-delimited text files with UniProt IDs when available.

and `expand_ortholog-uniprot_id.py` to expand lists to new rows

## add sequences w/ phosphosites to `phosphosite_orthology.db`
save TOTAL.elm in the same directory as the following script then
just run `dbPAF_txt_to_db.py` in `Extract_species_from_dbPAF` folder


## add orthologs to `phosphosite_orthology.db`

just run `pairwise_to_db.py` in `uniprot_PairwiseOrthologs` folder


## Merge oma orthologs with dbPAF info
`merge_oma_dbPAF.py`
use to create a new sqlite db of all the merged pairwise organism info
this is called `phosphosite_orthology_merged.db`


## remove amino acid mismatches
run `remove_letter_mismatches_db.py` this narrows the search space to only ortholog candidates with matching AA type (S:S,T:T,Y:Y; removed S:T etc...)
saves as `phosphosite_orthology_cleaned.db`


## alignment

run `align_species_biopython.py`
make sure that it is using `phosphosite_orthology_cleaned.db`
this database has all orthologous seqs in the same row as the human seq, allows for alignment and checking of the
phosphosite position. Saves each species as a new csv.

`homologous_df.to_csv(table_list[species_index][:5] + '_align_phos_matches_BioPy.csv', index=False)`




# CheckMyList.py

input csv:

my_human_uniprot_id		Position		Type
Q9UN37					97				S
Q9UI12					338				Y
Q8TDY2					222				S
P62241					69				S


outputs matrix of T/F whether or not id and site was found in other organism



# PSPS_DB_comparison.py
each phosphosite ortholog has a site group ID

SITE_GRP for AKT2:  2147001
exists for both human and mouse



# ToDo

- finish psp db comparison by including site with id 

- create main.py to run all scripts and automate downloads
- polish readme 

- tweak alignment parameters to increase psp match percentages
    - genetic programming/ automation?
	- at least automate the run/test so that i don't have to move files around
