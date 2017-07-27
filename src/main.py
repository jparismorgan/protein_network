import subprocess
import os, sys
import uniprot_dat_to_fasta
import blast_xml_to_fasta

from Tkinter import Tk
from UserInterface import UserInterface
from time import sleep

import datetime
import shutil
import glob

import pairwise_parser

def cleanProteinName(p_name):
    bad_chars = ['!', '@', '#', '$', '%','^','&','*','(',')','>','<', ' ']
    return ''.join([str(char) for char in p_name if char not in bad_chars])
        

def main():    
    mode = 1
    if mode == 1:
        home_filepath = "/Users/parismorgan/Desktop/iMicrobes/network_builder/"
        db_name = 'uniref90'
        protein = 'MDH-C.glutamicumlowKm'
        protein_seq = ">MDH-C.glutamicumlowKm \nMTTAAPQEFTAAVVEKFGHDVTVKDIDLPKPGPHQALVKVLTSGICHTDLHALEGDWPVKPEPPFVPGHEGVGEVVELGPGEHDVKVGDIVGNAWLWSACGTCEYCITGRETQCNEAEYGGYTQNGSFGQYMLVDTRYAARIPDGVDYLEAAPILCAGVTVYKALKVSETRPGQFMVISGVGGLGHIAVQYAAAMGMRVIAVDIADDKLELARKHGAEFTVNARNEDSGEAVQKYTNGGAHGVLVTAVHEAAFGQALDMARRAGTIVFNGLPPGEFPASVFNIVFKGLTIRGSLVGTRQDLAEALDFFARGLIKPTVSECSLDEVNGVLDRMRNGKIDGRVAIRF*"

        diamond_exec = home_filepath + "diamond-0.9.9/bin/diamond"   
    elif mode == 2:
        #Begin the python GUI
        top = Tk()
        gui = UserInterface(top)
        top.mainloop()
        
        #wait until ready to begin analysis
        while not gui.begin_analysis:
            sleep(1) 
        
        #read to begin analysis
        maindb_filepath = gui.maindb_filepath
        query_prot_filepath = gui.query_protein_sequence
        #TODO: Make a file of the query protein sequence, or specify opening a file.
    else:
        print "Please specify your mode of use."

    #Make new directory to save files in
    today = datetime.date.today()
    save_folder = home_filepath + 'files/' + today.strftime('%d%b%y_') + protein + '_01'
    while os.path.isdir(save_folder):
        save_folder = save_folder[:-2] + "%02d" %(int(save_folder[-2:]) + 1)
    os.mkdir(save_folder)
    save_folder = save_folder + '/'

    #Save our protein to that folder
    with open(save_folder+protein+'.fasta', 'w') as f:
        f.write(protein_seq)

    #Check if reference database exists
    if not os.path.isfile(home_filepath + db_name + '.dmnd'):
        print "The reference database does not exist. Please use 'makedb' to create it."
        return
        """
        Process for creating the db from the file downloaded from the uniprot website. 
        TODO: Automate the downloading and conversion and creation of this file.
    
        #Convert the .dat file (downloaded from UniProt) to a .fasta file    
        uniprot_dat_to_fasta.uniprot_dat_to_fasta(home_filepath+db_name+'.dat')
        #Build DIAMOND database of full bacterial ProtKB data from a fasta file
        action = "makedb --in " + home_filepath + db_name + ".fasta --db " + home_filepath + db_name
        command = '{0} {1}'.format(diamond_exec, action)
        subprocess.call(command, shell = True)
        """
    print "Found the reference database."

    #Blastp our AA sequence against the DIAMOND database. Output format 5 = BLAST XML.
    print "Blastp our AA sequence against the DIAMOND database. Output format 5 = BLAST XML"
    action = "blastp --db {0}{1}.dmnd --query {2}{3}.fasta --out {2}{1}_{3}.xml --outfmt 5  --max-target-seqs 1000 --compress 0".format(home_filepath, db_name, save_folder, protein)
    command = '{0} {1}'.format(diamond_exec, action)
    subprocess.call(command, shell=True)


    #Parse this XML file into a FASTA file.
    print "Parse this XML file into a FASTA file."
    save_folder_protein = save_folder + db_name + "_" + protein
    blast_xml_to_fasta.blast_xml_to_fasta(save_folder_protein+'.xml', save_folder_protein+'.fasta')
  
    #Build DIAMOND database of the 1000 sequences from out blastp search
    print "Build DIAMOND database of the 1000 sequences from out blastp search"
    action = "makedb --in {0}.fasta --db {0}".format(save_folder_protein)
    command = '{0} {1}'.format(diamond_exec, action)
    subprocess.call(command, shell=True)
   
    #Blastp our 1000 sequences against the DIAMOND database created from them. Functions as an all-against-all blast. Output format 0 = BLAST pairwise format.
    print "Blastp our 1000 sequences against the DIAMOND database created from them."
    action = "blastp --db {0}.dmnd --query {0}.fasta --out {0}_allvall --outfmt 0 --max-target-seqs 1000 --compress 0".format(save_folder_protein)
    command = '{0} {1}'.format(diamond_exec, action)
    subprocess.call(command, shell=True)

    #Can now call pairwise_parser.py to parse the all versus all result and create the cytoscope file
    print "Parse the all vs all result and create the graph"
    pairwise_parser.parseAllVsAllBlast(save_folder_protein+ '_allvall')
    pairwise_parser.createElementsFile(save_folder)

    #Copy network_base.html to the save folder
    print "Organize files"
    subprocess.call('cp ' + home_filepath + 'web/network_base.html ' + save_folder, shell = True);
    ##Move files to the new directory (Don't have to do this anymore. Check after fixing the physics sim)
    # for f in glob.glob(db_protein_path+'*'):
    #     shutil.copy(f, save_folder)
    print "Ready!"

if __name__ == '__main__':
    main()