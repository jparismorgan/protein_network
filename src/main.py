import subprocess
import os, sys
import uniprot_dat_to_fasta
import blast_xml_to_fasta

import datetime
import shutil
import glob

import pairwise_parser
import convertFastaToJs

def prepareAnalysis(home_filepath, db_name, protein, protein_seq):
    """
    Takes in the initial variables. 
    Creates new save directory and saves our protein as a .fasta file there
    Checks if reference DB exists
    Returns a ret_dict with Status (True = success, False = Error), message, exception,
        save_folder, and diamond_exec
    """
    #Initialize return dictionary
    ret_dict = {'status': None, 'message':None, 'exception':None, 'save_folder':None, 'diamond_exec':None}

    #Set up variables
    diamond_exec = home_filepath + 'diamond-0.9.9/bin/diamond'

    #Make new directory to save files in
    try:
        today = datetime.date.today()
        save_folder = home_filepath + 'files/' + today.strftime('%d%b%y_') + protein + '_01'
        while os.path.isdir(save_folder):
            save_folder = save_folder[:-2] + "%02d" %(int(save_folder[-2:]) + 1)
        os.mkdir(save_folder)
        save_folder = save_folder + '/'
    except Exception as e:
        ret_dict['status'] = False
        ret_dict['message'] = "Error creating new directory to save files in."
        ret_dict['exception'] = e
        return ret_dict

    # Save our protein to that folder
    try:
        with open(save_folder+protein+'.fasta', 'w') as f:
            f.write('>'+protein+'\n')
            f.write(protein_seq)
    except Exception as e:
        ret_dict['status'] = False
        ret_dict['message'] = "Error saving our protein to the save folder."
        ret_dict['exception'] = e
        return ret_dict
    
    # Check if reference database exists
    if not os.path.isfile(home_filepath + db_name + '.dmnd'):
        print "The reference database does not exist. Please use 'makedb' to create it."
        print "Attempted reference DB location: " + home_filepath + db_name + '.dmnd'
        ret_dict['status'] = False
        ret_dict['message'] = "The reference database does not exist. Please use 'makedb' to create it."
        return ret_dict
        """
        Process for creating the db from the file downloaded from the uniprot website. 
        TODO: Automate the downloading and conversion and creation of this file.
    
        # Convert the .dat file (downloaded from UniProt) to a .fasta file    
        uniprot_dat_to_fasta.uniprot_dat_to_fasta(home_filepath+db_name+'.dat')
        # Build DIAMOND database of full bacterial ProtKB data from a fasta file
        action = "makedb --in " + home_filepath + db_name + ".fasta --db " + home_filepath + db_name
        command = '{0} {1}'.format(diamond_exec, action)
        subprocess.call(command, shell = True)
        """

    # Check if diamond executable exists
    if not os.path.isfile(diamond_exec):
        print "The diamond executable does not exist. Check " + diamond_exec + " to see if it's there."
        ret_dict['status'] = False
        ret_dict['message'] = "The diamond executable does not exist. Check " + diamond_exec + " to see if it's there."
        return ret_dict

    ret_dict['status'] = True
    ret_dict['message'] = "Successfully found reference database & created save folder."
    ret_dict['save_folder'] = save_folder
    ret_dict['diamond_exec'] = diamond_exec
    return ret_dict

def blastAgainstReference(home_filepath, db_name, protein, diamond_exec, save_folder):
    ret_dict = {'status': None, 'message':None, 'exception':None, 'save_folder_protein':None}
    # Blastp our AA sequence against the DIAMOND database. Output format 5 = BLAST XML.
    try:
        action = "blastp --db {0}{1}.dmnd --query {2}{3}.fasta --out {2}{1}_{3}.xml --outfmt 5  --max-target-seqs 300 --compress 0".format(home_filepath, db_name, save_folder, protein)
        command = '{0} {1}'.format(diamond_exec, action)
        subprocess.call(command, shell=True)
    except Exception as e:
        ret_dict['status'] = False
        ret_dict['message'] = "Error in the blastp of our protein sequence against the reference database"
        ret_dict['exception'] = e
        return ret_dict
    
    # Parse this XML file into a FASTA file.
    try:    
        save_folder_protein = save_folder + db_name + "_" + protein
        blast_xml_to_fasta.blast_xml_to_fasta(save_folder_protein+'.xml', save_folder_protein+'.fasta')
    except Exception as e:
        ret_dict['status'] = False
        ret_dict['message'] = "Error in parsing the XML file into a FASTA file."
        ret_dict['exception'] = e
        return ret_dict

    ret_dict['status'] = True
    ret_dict['message'] = "Successful blastp against the reference database & conversion of the resulting XML file to a FASTA file."
    ret_dict['save_folder_protein'] = save_folder_protein
    return ret_dict
    
def allVsAll(diamond_exec, save_folder_protein):
    ret_dict = {'status': None, 'message':None, 'exception':None, 'save_folder_protein':None}

    # Build DIAMOND database of the 1000 sequences from our blastp search
    try:
        print "Build DIAMOND database of the 1000 sequences from our blastp search"
        action = "makedb --in {0}.fasta --db {0}".format(save_folder_protein)
        command = '{0} {1}'.format(diamond_exec, action)
        subprocess.call(command, shell=True)
    except Exception as e:
        ret_dict['status'] = False
        ret_dict['message'] = "Error in building DIAMOND database of the 1000 sequences from our blastp search."
        ret_dict['exception'] = e
        return ret_dict
    
    # Blastp our 1000 sequences against the DIAMOND database created from them. Functions as an all-against-all blast. Output format 0 = BLAST pairwise format.
    try:
        print "Blastp our 1000 sequences against the DIAMOND database created from them."
        action = "blastp --db {0}.dmnd --query {0}.fasta --out {0}_allvall --outfmt 0 --max-target-seqs 300 --compress 0".format(save_folder_protein)
        command = '{0} {1}'.format(diamond_exec, action)
        subprocess.call(command, shell=True)
    except Exception as e:
        ret_dict['status'] = False
        ret_dict['message'] = "Error in blastp our sequences against the DIAMOND database created from them."
        ret_dict['exception'] = e
        return ret_dict

    ret_dict['status'] = True
    ret_dict['message'] = "Successfull all-versus-all blastp search."
    return ret_dict

def organizeNetwork(home_filepath, db_name, protein, diamond_exec, save_folder, save_folder_protein):
    ret_dict = {'status': None, 'message':None, 'exception':None, 'save_folder_protein':None}
    
    # Can now call pairwise_parser.py to parse the all versus all result and create the network.js file of edges and nodes
    try:
        print "Parse the all vs all result and create the graph"
        pairwise_parser.parseAllVsAllBlast(save_folder_protein+ '_allvall')
        pairwise_parser.createElementsFile(save_folder)
    except Exception as e:
        ret_dict['status'] = False
        ret_dict['message'] = "Error in parsing the all vs all result and create the graph"
        ret_dict['exception'] = e
        return ret_dict

    # Create javascript variable containing objects of nodes to protein sequences
    try:
        print "Create protein accession number to protein sequence objects for use in visualization."
        convertFastaToJs.convertFastaToJs(save_folder, db_name, protein)
        pairwise_parser.createElementsFile(save_folder)
    except Exception as e:
        ret_dict['status'] = False
        ret_dict['message'] = "Error in using protein accession number to create protein:sequence pair objects for use in visualization"
        ret_dict['exception'] = e
        return ret_dict
    
    #Copy network_base.html to the save folder
    try:
        print "Organize files"
        subprocess.call('cp ' + home_filepath + 'web/network_base.html ' + save_folder+'network_'+protein+'.html', shell = True)
    except Exception as e:
        ret_dict['status'] = False
        ret_dict['message'] = "Error in copying network_base.html to the save folder."
        ret_dict['exception'] = e
        return ret_dict



    ret_dict['status'] = True
    ret_dict['message'] = "Successfull organization of files for the network."
    return ret_dict

# if __name__ == '__main__':
#     home_filepath = "/Users/parismorgan/Desktop/iMicrobes/network_builder"
#     db_name = 'uniref90'
#     protein = 'mmox'
#     das1_seq = "MALAKAASINDDIHDLTMRAFRCYVLDLVEQYEGGHPGSAMGMVAMGIALWKYTMKYSTNDPTWFNRDRFVLSNGHVCLFQYLFQHLSGLKSMTEKQLKSYHSSDYHSKCPGHPEIENEAVEVTTGPLGQGISNSVGLAIASKNLGALYNKPGYEVVNNTTYCIVGDACLQEGPALESISFAGHLGLDNLVVIYDNNQVCCDGSVDIANTEDISAKFRACNWNVIEVEDGARDVATIVKALELAGAEKNRPTLINVRTIIGTDSAFQNHCAAHGSALGEEGIRELKIKYGFNPSQKFHFPQEVYDFFSDIPAKGDEYVSNWNKLVSSYVKEFPELGAEFQSRVKGELPKNWKSLLPNNLPNEDTATRTSARAMVRALAKDVPNVIAGSADLSVSVNLPWPGSKYFENPQLATQCGLAGDYSGRYVEFGIREHCMCAIANGLAAFNKGTFLPITSSFYMFYLYAAPALRMAALQELKAIHIATHDSIGAGEDGPTHQPIAQSALWRAMPNFYYMRPGDASEVRGLFEKAVELPLSTLFSLSRHEVPQYPGKSSIELAKRGGYVFEDAKDADIQLIGAGSELEQAVKTARILRSRGLKVRILSFPCQRLFDEQSVGYRRSVLQRGKVPTVVIEAYVAYGWERYATAGYTMNTFGKSLPVEDVYEYFGFNSSEISKKIEGYVRAVKANPDLLYEFIDLTEKPKHDQNHL*"
#     mmox_seq = "MALSTATKAATDALAANRAPTSVNAQEVHRWLQSFNWDFKNNRTKYATKYKMANETKEQFKLIAKEYARMEAVKDERQFGSLQDALTRLNAGVRVHPKWNETMKVVSNFLEVGEYNAIAATGMLWDSAQAAEQKNGYLAQVLDEIRHTHQCAYVNYYFAKNGQDPAGHNDARRTRTIGPLWKGMKRVFSDGFISGDAVECSLNLQLVGEACFTNPLIVAVTEWAAANGDEITPTVFLSIETDELRHMANGYQTVVSIANDPASAKYLNTDLNNAFWTQQKYFTPVLGMLFEYGSKFKVEPWVKTWNRWVYEDWGGIWIGRLGKYGVESPRSLKDAKQDAYWAHHDLYLLAYALWPTGFFRLALPDQEEMEWFEANYPGWYDHYGKIYEEWRARGCEDPSSGFIPLMWFIENNHPIYIDRVSQVPFCPSLAKGASTLRVHEYNGQMHTFSDQWGERMWLAEPERYECQNIFEQYEGRELSEVIAELHGLRSDGKTLIAQPHVRGDKLWTLDDIKRLNCVFKNPVKAFN*"
#     diamond_exec = home_filepath + "/diamond-0.9.9/bin/diamond"   
#     main(home_filepath, db_name, protein, mmox_seq, diamond_exec)


    # def main(home_filepath, db_name, protein, protein_seq):    
    # home_filepath += '/'
    # diamond_exec = home_filepath + 'diamond-0.9.9/bin/diamond'
    # protein = cleanProteinName(protein)
    # print home_filepath, db_name, protein, protein_seq, diamond_exec

    # #Make new directory to save files in
    # today = datetime.date.today()
    # save_folder = home_filepath + 'files/' + today.strftime('%d%b%y_') + protein + '_01'
    # while os.path.isdir(save_folder):
    #     save_folder = save_folder[:-2] + "%02d" %(int(save_folder[-2:]) + 1)
    # os.mkdir(save_folder)
    # save_folder = save_folder + '/'

    # #Save our protein to that folder
    # with open(save_folder+protein+'.fasta', 'w') as f:
    #     f.write('>'+protein+'\n')
    #     f.write(protein_seq)

    # #Check if reference database exists
    # if not os.path.isfile(home_filepath + db_name + '.dmnd'):
    #     print "The reference database does not exist. Please use 'makedb' to create it."
    #     return
    #     """
    #     Process for creating the db from the file downloaded from the uniprot website. 
    #     TODO: Automate the downloading and conversion and creation of this file.
    
    #     #Convert the .dat file (downloaded from UniProt) to a .fasta file    
    #     uniprot_dat_to_fasta.uniprot_dat_to_fasta(home_filepath+db_name+'.dat')
    #     #Build DIAMOND database of full bacterial ProtKB data from a fasta file
    #     action = "makedb --in " + home_filepath + db_name + ".fasta --db " + home_filepath + db_name
    #     command = '{0} {1}'.format(diamond_exec, action)
    #     subprocess.call(command, shell = True)
    #     """
    # print "Found the reference database."

    # #Blastp our AA sequence against the DIAMOND database. Output format 5 = BLAST XML.
    # print "Blastp our AA sequence against the DIAMOND database. Output format 5 = BLAST XML"
    # action = "blastp --db {0}{1}.dmnd --query {2}{3}.fasta --out {2}{1}_{3}.xml --outfmt 5  --max-target-seqs 300 --compress 0".format(home_filepath, db_name, save_folder, protein)
    # command = '{0} {1}'.format(diamond_exec, action)
    # subprocess.call(command, shell=True)

    # #Parse this XML file into a FASTA file.
    # print "Parse this XML file into a FASTA file."
    # save_folder_protein = save_folder + db_name + "_" + protein
    # blast_xml_to_fasta.blast_xml_to_fasta(save_folder_protein+'.xml', save_folder_protein+'.fasta')
  
    # #Build DIAMOND database of the 1000 sequences from out blastp search
    # print "Build DIAMOND database of the 1000 sequences from out blastp search"
    # action = "makedb --in {0}.fasta --db {0}".format(save_folder_protein)
    # command = '{0} {1}'.format(diamond_exec, action)
    # subprocess.call(command, shell=True)
   
    # #Blastp our 1000 sequences against the DIAMOND database created from them. Functions as an all-against-all blast. Output format 0 = BLAST pairwise format.
    # print "Blastp our 1000 sequences against the DIAMOND database created from them."
    # action = "blastp --db {0}.dmnd --query {0}.fasta --out {0}_allvall --outfmt 0 --max-target-seqs 300 --compress 0".format(save_folder_protein)
    # command = '{0} {1}'.format(diamond_exec, action)
    # subprocess.call(command, shell=True)

    # #Can now call pairwise_parser.py to parse the all versus all result and create the cytoscope file
    # print "Parse the all vs all result and create the graph"
    # pairwise_parser.parseAllVsAllBlast(save_folder_protein+ '_allvall')
    # pairwise_parser.createElementsFile(save_folder)

    # #Copy network_base.html to the save folder
    # print "Organize files"
    # subprocess.call('cp ' + home_filepath + 'web/network_base.html ' + save_folder+'network_'+protein+'.html', shell = True)
    # ##Move files to the new directory (Don't have to do this anymore. Check after fixing the physics sim)
    # # for f in glob.glob(db_protein_path+'*'):
    # #     shutil.copy(f, save_folder)
    # print "Ready!"
