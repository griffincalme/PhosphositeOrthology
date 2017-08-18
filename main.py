import time
import urllib.request
import zipfile
import tarfile
import os
import shutil
from extract_species_from_dbPAF_to_txt import extract_species_from_dbPAF_to_txt

#from extract_species_from_dbPAF import extract_species_from_dbPAF
from dbPAF_txt_to_db import dbPAF_txt_to_db
from pairwise_to_uniprot import pairwise_to_uniprot
from expand_ortholog_uniprot_id import expand_ortholog_uniprot_id
from pairwise_to_db import pairwise_to_db
from merge_oma_dbPAF import merge_oma_dbPAF
from remove_letter_mismatches_db import remove_letter_mismatches_db
from align_species_biopython import align_species_biopython



print('Downloading dbPAF Total')
url = 'http://dbpaf.biocuckoo.org/TOTAL.zip'
if os.path.isfile('TOTAL.elm'):
    print('TOTAL.elm already exists in local directory')
else:
    urllib.request.urlretrieve(url)
    print('\nUnzipping TOTAL.elm')
    zip = zipfile.ZipFile(r'TOTAL.zip')
    zip.extractall(r'')
    os.remove('TOTAL.zip')


if os.path.isfile('phosphosite_orthology_cleaned.db'):
    print('phosphosite_orthology_cleaned.db already exists, delete or move it if you\'d like to regenerate the database')
else:

    print('\nExtracting CAEEL, DROME, HUMAN, MOUSE, RATNO, POMBE, and YEAST from TOTAL.elm')
    print('to \'extract_species_from_dbPAF/\' ...')

    # consider going straight from df to sql without making intermediate text files, would need to combine
    # extract_species_from_dbPAF and dbPAF_txt_to_db
    extract_species_from_dbPAF_to_txt()


    #extract_species_from_dbPAF()
    print('\nGenerating SQLite database with dbPAF files...')
    dbPAF_txt_to_db()
    shutil.rmtree('extract_species_from_dbPAF')


    print('\nSee readme steps about OMA ortholog search')

    #oma_url = http://omabrowser.org/media/AllAllExport/AllAllExport-696325701.tgz
    #urllib.request.urlretrieve(oma_url)

    #tar = tarfile.open('AllAllExport-696325701.tgz')
    #tar.extractall()
    #tar.close()

    '''
    print('\nDownloading OMA to UniProt ID conversion table...')
    url_id_table = 'http://omabrowser.org/All/oma-uniprot.txt.gz'
    if os.path.isfile('oma-uniprot.txt'):
        print('oma-uniprot.txt already exists in local directory')
    else:
        urllib.request.urlretrieve(url_id_table)
        print('\nUnzipping oma-uniprot.txt.gz')
        #tar = tarfile.open('oma-uniprot.txt.gz')
        #tar.extractall()
        #tar.close()
    '''

    print('\nPlease download and unzip http://omabrowser.org/All/oma-uniprot.txt.gz into PhosphositeOrthology/')

    print('\nConverting OMA IDs to UniProt IDs in pairwise ortholog files...')
    pairwise_to_uniprot()
    print('Saved as uniprot_PairwiseOrthologs/')
    shutil.rmtree('OMAPairwiseOrthologs')

    print('\nExpanding synonymous UniProt IDs to new rows...')
    expand_ortholog_uniprot_id()

    print('\nAdding ortholog pairs to SQLite database...')
    pairwise_to_db()
    shutil.rmtree('uniprot_PairwiseOrthologs')


    print('\nMerging OMA orthologs with dbPAF data...')
    merge_oma_dbPAF()
    os.remove('phosphosite_orthology.db')

    print('\nRemoving amino acid mismatches to reduce search space for alignment')
    remove_letter_mismatches_db()
    os.remove('phosphosite_orthology_merged.db')


print('\nRunning alignment to remove non-phosphosite orthologs from pairwise gene orthologs')
align_species_biopython()


print('Done, use CheckMyList.py')
