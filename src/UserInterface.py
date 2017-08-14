"""
Runs the Tkinter UI for the tool
Has a main analysis option and a further analysis option
----------------------------------------------------------------
Industrial Microbes C 2017 All Rights Reserved
Contact: J Paris Morgan (jparismorgan@gmail.com) or Derek Greenfield (derek@imicrobes.com)
"""
from Tkinter import Tk, Label, Button, BOTTOM, Frame, Text, RIDGE, END
import tkFileDialog
import re
import diamond_caller
import time
import webbrowser
import os
import subprocess
import requests
import xml.etree.ElementTree as ET

WIDTH = 650
HEIGHT = 800

class UserInterface:
    def __init__(self, master):
        # initialize variables
        self.master = master
        self.home_directory_path = None
        self.analysis_home_directory_path = None
        self.analysis_file_path = None
        self.begin_analysis = False

        # Frame.__init__(self, master)

        # window settings
        master.title("Network Builder")
        master.resizable(width=False, height=False)
        master.configure(bg = "white")
        master.grid()
        master.geometry('{}x{}'.format(WIDTH, HEIGHT))

        ################################################################################

        #Title 
        self.title_label = Label(master, text="Main Analysis Workflow",font= "-weight bold")
        self.title_label.pack(pady = 2)

        # Instructions label
        self.instuctions_label = Label(master, text="Enter the name of you protein sequence")
        self.instuctions_label.pack(pady = 2)
        
        # Text entry box: prot_name
        self.prot_name = Text(master, height=1, width=50, bg="#cdc9c9", bd = 1, relief=RIDGE, highlightthickness=0)
        self.prot_name.pack(pady = 2)

        #Instructions label
        self.instuctions_label = Label(master, text="Enter your protein sequence")
        self.instuctions_label.pack(pady = 2)

        #Text entry box: prot_seq
        self.prot_seq = Text(master, height=10, width=50, bg="#cdc9c9", bd = 1, relief=RIDGE, highlightthickness=0)
        self.prot_seq.pack(pady = 2)

        #Instructions label
        self.directory_label = Label(master, text="Select location of your 'network_builder' directory")
        self.directory_label.pack(pady = 2)

        #Get home directory location
        self.get_home_directory_button = Button(master, text = "Click to navigate", command=self.getHomeDirectoryPath)
        self.get_home_directory_button.pack(pady = 2) 

        #Instructions label
        self.instuctions_label = Label(master, text="Enter the name of your reference database (default: uniref90)")
        self.instuctions_label.pack(pady = 2)

        #Text entry box: db_name
        self.db_name = Text(master, height=1, width=50, bg="#cdc9c9", bd = 1, relief=RIDGE, highlightthickness=0)
        self.db_name.pack(pady = 2)
        self.db_name.insert(END, "uniref90")
        
        #Label to use for errors & info
        self.main_info_label = Label(master, text="Follow all steps above and then press 'Begin Analysis'")
        self.main_info_label.pack(pady = 2)

        #Run button
        self.play_button = Button(master, text = "Begin analysis", command=self.checkStartAnalysis)
        self.play_button.pack(pady = 2) 

        ################################################################################

        #Black bar separation
        self.f=Frame(master,height=3,width=500,bg="black")
        self.f.pack()

        #Further Analysis Title
        self.analysis_label = Label(master, text="Further Analysis on Existing FASTA Files",font= "-weight bold")
        self.analysis_label.pack(pady = 2)

        #Instructions label
        self.analysis_directory_label = Label(master, text="Select location of your 'network_builder' directory")
        self.analysis_directory_label.pack(pady = 2)

        #Get home directory location
        self.analysis_get_home_directory_button = Button(master, text = "Click to navigate", command=self.getHomeDirectoryPathAnalysis)
        self.analysis_get_home_directory_button.pack(pady = 2) 

        #Analysis Instructions
        self.analysis_instructions_label = Label(master, text="Select the file that you downloaded on the network visualization page.")
        self.analysis_instructions_label.pack(pady = 2)

        #Select further analysis file
        self.get_analysis_file_button = Button(master, text = "Click to navigate", command=self.getAnalysisFile)
        self.get_analysis_file_button.pack(pady = 2) 

        #Analysis Instructions
        self.analysis_info_label = Label(master, text="Now choose an analysis option:")
        self.analysis_info_label.pack(pady = 2)

        #Run representative nodes button
        self.analysis_rep_button = Button(master, text = "Analyze representative nodes only", command = lambda:self.analyzeProteins(False) ) 
        self.analysis_rep_button.pack(pady = 2) 

        #Run representative nodes and their clusters button
        self.analysis_repcluster_button = Button(master, text = "Analyze representative nodes and their associated cluster proteins", command= lambda:self.analyzeProteins(True))
        self.analysis_repcluster_button.pack(pady = 2) 

        ################################################################################

        #Black bar separation
        self.f=Frame(master,height=3,width=500,bg="black")
        self.f.pack()

        #Info Box Title
        self.status_label = Label(master, text="Status Box",font= "-weight bold")
        self.status_label.pack(pady = 2)

        #Label to use for errors & info
        self.status_label = Label(master, text="")
        self.status_label.pack(pady = 2)

        #Label to display the resulting html file
        self.link = Label(master, text="\n", fg="blue", cursor="hand2")
        self.link.pack(pady = 2)

        #Copyright label
        self.copright_label = Label(master, text="Copyright C 2017 Industrial Microbes, Inc. All Rights Reserved.")
        self.copright_label.pack(side=BOTTOM, pady = 2)
    
#Main helper functions
    def writeToMainInfoLabel(self, message):
        self.main_info_label.config(text = message)
    def writeToStatusLabel(self, message):
        self.status_label.config(text = message) 
    def openHTML(self, event, text):
        webbrowser.open_new(text)
        
    def getHomeDirectoryPath(self):
        """
        Gets the path to the maindb.db directory. Sets it as a variable of user_interface.
        """
        self.home_directory_path = tkFileDialog.askdirectory()
        self.directory_label.config(text =  'Directory: ' + self.home_directory_path)
    


    def is_protein(self,in_str):
        """
        Determine if string is a valid protein sequence; it's valid if it only contains {ACGTRNDQEHILKMFPSWYV} characters.
        """
        if re.findall(r"^[ACGTRNDQEHILKMFPSWYV*]+$", in_str):
            return True
        else:
            return False
    
    def cleanProteinName(self, p_name): 
        bad_chars = ['!', '@', '#', '$', '%','^','&','*','(',')','>','<', ' ']
        return ''.join([str(char) for char in p_name if char not in bad_chars]).strip()
#Analysis helper functions
    def getHomeDirectoryPathAnalysis(self):
        """
        Gets the path to the home directory. Sets it as a variable of user_interface.
        """
        self.analysis_home_directory_path = tkFileDialog.askdirectory()
        self.analysis_directory_label.config(text =  'Directory: ' + self.analysis_home_directory_path)
    def getAnalysisFile(self):
        """
        Gets the path to the further analysis file. Sets it as a variable of user_interface.
        """
        self.analysis_file_path = tkFileDialog.askopenfilename()
        self.analysis_instructions_label.config(text =  'Analysis file: ' + self.analysis_file_path)
    def getClusterFastaFromProtein(self, save_folder_protein, protein_name):
        """
        Calls the UniRef database with the protein name.
        If no response, it is no longer the cluster representative 
                --> Call UniProt, scrape site, and get cluster rep
        Parse the information about the rep member and each of the cluster members
        Return a representative node with information and a list of cluster nodes
        """
        # API call to UniRef DB
        base_url = "http://www.uniprot.org/uniref/"
        extension = ".xml"
        my_response = requests.get(base_url + protein_name + extension)
        # For successful API call, response code will be 200 (OK)
        if not my_response.ok:
            print protein_name
            # If response code is not ok (200), the cluster is not valid. We will search for the protein in the UniProt DB
            # Assuming a structure of: UniRef90_proteinname_specificid
            stripped_protein_name = protein_name.split('_')[1]
            url = "http://www.uniprot.org/uniref/?query=uniprot:" + \
                stripped_protein_name + "*&fil=identity:0.9&sort=score"
            my_response = requests.get(url)
            # For successful API call, response code will be 200 (OK)
            if not my_response.ok:
                print (my_response.status_code)
                # If response code is not ok (200), print the resulting http error code with description. The protein sequence was not in UniProt
                my_response.raise_for_status()

            # We have found the protein in the UniProt DB. We will parse the html page to get the protein that is the cluster representative
            temp = re.findall('id="UniRef90_.*?"', my_response.content)
            if len(temp) == 0:
                print "Error in Userinterface -> getClusterFastaFromProtein when calling the uniref DB on our cluster protein"
            else:
                protein_name = temp[0].replace('"', '').split('=')[-1]
            my_response = requests.get(base_url + protein_name + extension)
            if not my_response.ok:
                print (my_response.status_code)
                # If response code is not ok (200), print the resulting http error code with description. The protein sequence was not in UniProt
                my_response.raise_for_status()

        # get root of the XML response
        root = ET.fromstring(my_response.content)

        with open(save_folder_protein + '_plusclusters.fasta', 'a') as out_file:
            
            # Get the representative member
            rep_member = root.find('{http://uniprot.org/uniref}entry').find(
            '{http://uniprot.org/uniref}representativeMember').find('{http://uniprot.org/uniref}dbReference')
            prot_fasta = requests.get("http://www.uniprot.org/uniprot/"+rep_member.attrib['id']+".fasta")

            out_file.write(prot_fasta.text.encode('ascii', 'ignore'))           # Unicode to ascii. Ignore unicode characters that can't be converted

            for i in root.iter(tag='{http://uniprot.org/uniref}member'):
                member = i.find('{http://uniprot.org/uniref}dbReference')
                #print "http://www.uniprot.org/uniprot/"+member.attrib['id']+".fasta"
                prot_fasta = requests.get("http://www.uniprot.org/uniprot/"+member.attrib['id']+".fasta")
                if re.search('Sorry', prot_fasta.text):
                    # Not found in UniProt, so try UniParc
                    #print "http://www.uniprot.org/uniparc/"+member.attrib['id']+".fasta"
                    prot_fasta = requests.get("http://www.uniprot.org/uniparc/"+member.attrib['id']+".fasta")
                    #print prot_fasta
                if not re.search('Sorry', prot_fasta.text):
                    # If found in UniProt or UniParc write to file
                    out_file.write(prot_fasta.text.encode('ascii', 'ignore'))   # Unicode to ascii. Ignore unicode characters that can't be converted

        return


#General purpose functions. Use allvall_parser.py
    def guiPrepareAnalysis(self):
        """
        Begin analysis
        """
        self.home_directory_path += '/'

        #Set up save directory, protein .fasta file, and diamond_exec file
        analysis_dict = diamond_caller.prepareAnalysis(self.home_directory_path, self.reference_db_name, self.query_protein_sequence_name, self.query_protein_sequence)
        if not analysis_dict['status']:
            self.writeToStatusLabel(ret_dict['message'] + "\n Ending program. Please try again")
            print analysis_dict['exception']
            return
        self.save_folder = analysis_dict['save_folder']
        self.diamond_exec = analysis_dict['diamond_exec']
        self.status_label.config(text = analysis_dict['message'] + "\n Will now blast the protein against the reference database." )
        self.master.after(1000, self.guiBlastAgainstReference)

    def guiBlastAgainstReference(self):
        #blast protein against reference DB
        protein_ref_dict = diamond_caller.blastAgainstReference(self.home_directory_path, self.reference_db_name, self.query_protein_sequence_name, self.diamond_exec, self.save_folder)
        if not protein_ref_dict['status']:
            self.writeToStatusLabel(protein_ref_dict['message'] + "\n Ending program. Please try again")
            print protein_ref_dict['exception']
            return
        self.save_folder_protein = protein_ref_dict['save_folder_protein']
        self.writeToStatusLabel(protein_ref_dict['message'] + "\n Will now make a database of the sequences from the blastp and then do an all versus all blastp. \n This can take 5-10 minutes; Don't close this window or the program will end early.")

        self.master.after(1000, self.guiAllVsAll)
        #all_vs_all_dict = diamond_caller.allVsAll(self.home_directory_path, self.reference_db_name, self.query_protein_sequence_name, diamond_exec, save_folder, save_folder_protein)

    def guiAllVsAll(self):
        allvsall_ref_dict = diamond_caller.allVsAll(self.diamond_exec, self.save_folder_protein)
        if not allvsall_ref_dict['status']:
            self.writeToStatusLabel(allvsall_ref_dict['message'] + "\n Ending program. Please try again")
            print allvsall_ref_dict['exception']
            return
        self.writeToStatusLabel(allvsall_ref_dict['message'] + "\n Will now organize some files.")
        self.master.after(1000, self.guiOrganizeNetwork)

    def guiOrganizeNetwork(self):
        organize_network_ref_dict = diamond_caller.organizeNetwork(self.home_directory_path, self.query_protein_sequence_name, self.save_folder, self.save_folder_protein)
        if not organize_network_ref_dict['status']:
            self.writeToStatusLabel(organize_network_ref_dict['message'] + "\n Ending program. Please try again")
            print organize_network_ref_dict['exception']
            return
        
        #User instructions
        self.writeToStatusLabel(organize_network_ref_dict['message'] + "\n All done! Click the link below to open. Copy file into Chrome if not default.")

        # # Debug
        # self.save_folder = "/Users/parismorgan/Desktop/iMicrobes/network_builder/files/08Aug17_solmethanemonosubunitA_01/"
        # self.query_protein_sequence_name = "solmethanemonosubunitA"

        # Write link to GUI so user can open html file
        self.link.config(text = "file://"+self.save_folder+'\n network_'+self.query_protein_sequence_name+'.html')
        self.link.bind("<1>", lambda event, text="file://"+self.save_folder+'network_'+self.query_protein_sequence_name+'.html': self.openHTML(event, text))
       
#Start function for analyzing representative nodes
    def analyzeProteins(self, cluster):
        self.writeToStatusLabel("Begininng analysis.")
        
        # check we have the home directory file path
        if not self.analysis_home_directory_path:
            self.writeToStatusLabel("Error! Select the 'network_builder' directory. ")
            return
        
        # check we have analysis file
        if not self.analysis_file_path:
            self.writeToStatusLabel("Error! Select an analysis file.")
            return
        try :
            analysis_file = open(self.analysis_file_path, 'r')
            analysis_file.close()
            self.writeToStatusLabel("Success in opening analysis file")
        except IOError:
            self.writeToStatusLabel("Error! Could not open analysis file.")
            return
        
        # set up diamond executable path
        self.home_directory_path = self.analysis_home_directory_path + '/'
        self.diamond_exec = self.home_directory_path + 'diamond-0.9.9/bin/diamond'
        
        #create a new save folder at /path_to_analysis_file/analysis01/
        #move the analysis file into that folder
        try:
            self.save_folder = '/'.join(self.analysis_file_path.split('/')[:-1]) + '_analysis_01'
            
            self.query_protein_sequence_name = self.analysis_file_path.split('/')[-1].split('.')[0]
            while os.path.isdir(self.save_folder):
                self.save_folder = self.save_folder[:-2] + "%02d" %(int(self.save_folder[-2:]) + 1)
            os.mkdir(self.save_folder)
            self.save_folder = self.save_folder + '/'
            subprocess.call("cp " + self.analysis_file_path + " " + self.save_folder + self.query_protein_sequence_name + '.fasta', shell = True)
            self.writeToStatusLabel("Location of files " + self.save_folder)
        except Exception as e:
            self.writeToStatusLabel("Couldn't set up process. See console.")
            print e
            return

        self.save_folder_protein = self.save_folder + self.query_protein_sequence_name

        # Create the match protein file so don't throw errors in network.js
        try:
            match_protein_file = '/'.join(self.analysis_file_path.split('/')[:-1]) + '/match_protein.js'
            subprocess.call('cp ' + match_protein_file + ' ' + self.save_folder + 'match_protein.js', shell = True)
        except Exception as e:
            self.writeToStatusLabel("Couldn't create empty match protein file.")
            print e
            return    

        # Check whether we need to download all the cluster node sequences from UniProt
        uniref = False
        if cluster:
            self.writeToStatusLabel("Fetching the proteins associated with the cluster and reps")
            with open(self.save_folder_protein + '.fasta', 'r') as rep_protein_file, open(self.save_folder + 'match_protein.js', 'a') as match_protein_save_file:
                match_protein_save_file.write('\n \n var analysis_proteins = [ \n')
                for line in rep_protein_file:
                    if line.strip()[0] == ">":
                        # Parse the analysis file for the name
                        protein_name = line.strip().split("|")[1]
                        alternate_name = line.strip().split("|")[0][1:]

                        # Add the protein to the match_protein.js file in the analysis_proteins array
                        match_protein_save_file.write('{id: "' + protein_name + '", UniProtKB_accession: "' + alternate_name + '" },\n' )

                        if re.search('UniRef', line):
                            # Get clusters from the uniref database
                            self.getClusterFastaFromProtein(self.save_folder_protein, protein_name)
                            uniref = True
                if uniref:
                    self.save_folder_protein = self.save_folder_protein + "_plusclusters"

                match_protein_save_file.write('] \n')
            

        #all vs all blast call
        self.guiAllVsAll() 
        return
        

#Start function for the main program
    def checkStartAnalysis(self):
        """
        Checks if   1) we have the path to the maindb.db file
                    2) the entered sequence is >19 characters and is a valid AA sequence
        Once we have, call startAnalysis() to begin analysis

        """
        self.main_info_label.config(text = "")
        self.link.config(text = "")

        self.query_protein_sequence = self.prot_seq.get("1.0",END)

        self.reference_db_name = self.db_name.get("1.0",END).strip()

        #check for a protein name
        self.query_protein_sequence_name = self.prot_name.get("1.0",END)
        self.query_protein_sequence_name = self.cleanProteinName(self.query_protein_sequence_name)
        if len(self.query_protein_sequence_name) <= 2:
            print self.query_protein_sequence_name
            self.writeToMainInfoLabel("Error! Your sequence name looks too short.")

        # check the prot_seq text box for a  valid protein sequence
        elif len(self.query_protein_sequence) <= 19:
            self.writeToMainInfoLabel("Error! Your sequence looks too short.")
        elif not self.is_protein(self.query_protein_sequence):
            self.writeToMainInfoLabel("This doesn't look like a valid protein sequence. Try again!")
            
        # check we have the home directory file path
        elif not self.home_directory_path:
            self.writeToMainInfoLabel("Error! Select the 'maindb.db' file. ")
        
        # check for db name
        elif len(self.reference_db_name) <= 1:
            self.writeToMainInfoLabel("Error! Your database name looks too short.")

        else:
            # we can begin analysis
            self.writeToMainInfoLabel("Running")
            self.guiPrepareAnalysis()
            

if __name__ == '__main__':
    top = Tk()
    gui = UserInterface(top)
    top.mainloop()