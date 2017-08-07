from Tkinter import Tk, Label, Button, BOTTOM, Frame, Text, RIDGE, END
import tkFileDialog
import re
import main
import time

WIDTH = 600
HEIGHT = 500

class UserInterface:
    def __init__(self, master):
        # initialize variables
        self.master = master
        self.home_directory_path = None
        self.begin_analysis = False

        # Frame.__init__(self, master)

        # window settings
        master.title("Network Builder")
        master.resizable(width=False, height=False)
        master.configure(bg = "white")
        master.grid()
        master.geometry('{}x{}'.format(WIDTH, HEIGHT))

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

        #Get main.db location
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
        self.info_label = Label(master, text="Follow all steps above and then press 'Begin Analysis'")
        self.info_label.pack(pady = 2)

        #Run button
        self.play_button = Button(master, text = "Begin analysis", command=self.checkStartAnalysis)
        self.play_button.pack(pady = 2) 

        #Label to use for errors & info
        self.status_label = Label(master, text="")
        self.status_label.pack(pady = 2)

        #Copyright label
        self.copright_label = Label(master, text="Copyright C 2017 Industrial Microbes, Inc. All Rights Reserved.")
        self.copright_label.pack(side=BOTTOM, pady = 2)
    
    def writeToInfoBox(self, message):
        self.info_label.config(text = message)
    def writeToStatusBox(self, message):
        self.status_label.config(text = message)

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
       
    
    def guiPrepareAnalysis(self):
        """
        Begin analysis
        """
        self.home_directory_path += '/'

        #Set up save directory, protein .fasta file, and diamond_exec file
        analysis_dict = main.prepareAnalysis(self.home_directory_path, self.reference_db_name, self.query_protein_sequence_name, self.query_protein_sequence)
        if not analysis_dict['status']:
            self.writeToStatusBox(ret_dict['message'] + "\n Ending program. Please try again")
            print analysis_dict['exception']
            return
        self.save_folder = analysis_dict['save_folder']
        self.diamond_exec = analysis_dict['diamond_exec']
        self.status_label.config(text = analysis_dict['message'] + "\n Will now blast the protein against the reference database." )
        self.master.after(1000, self.guiBlastAgainstReference)

    def guiBlastAgainstReference(self):
        #blast protein against reference DB
        protein_ref_dict = main.blastAgainstReference(self.home_directory_path, self.reference_db_name, self.query_protein_sequence_name, self.diamond_exec, self.save_folder)
        if not protein_ref_dict['status']:
            self.writeToStatusBox(protein_ref_dict['message'] + "\n Ending program. Please try again")
            print protein_ref_dict['exception']
            return
        self.save_folder_protein = protein_ref_dict['save_folder_protein']
        self.writeToStatusBox(protein_ref_dict['message'] + "\n Will now make a database of the sequences from the blastp and then do an all versus all blastp. \n This can take 5-10 minutes; Don't close this window or the program will end early.")

        self.master.after(1000, self.guiAllVsAll)
        #all_vs_all_dict = main.allVsAll(self.home_directory_path, self.reference_db_name, self.query_protein_sequence_name, diamond_exec, save_folder, save_folder_protein)

    def guiAllVsAll(self):
        allvsall_ref_dict = main.allVsAll(self.diamond_exec, self.save_folder_protein)
        if not allvsall_ref_dict['status']:
            self.writeToStatusBox(allvsall_ref_dict['message'] + "\n Ending program. Please try again")
            print allvsall_ref_dict['exception']
            return
        self.writeToStatusBox(allvsall_ref_dict['message'] + "\n Will now organize some files. This should be very quick.")
        self.master.after(1000, self.guiOrganizeNetwork)

    def guiOrganizeNetwork(self):
        organize_network_ref_dict = main.organizeNetwork(self.home_directory_path, self.reference_db_name, self.query_protein_sequence_name, self.diamond_exec, self.save_folder, self.save_folder_protein)
        if not organize_network_ref_dict['status']:
            self.writeToStatusBox(organize_network_ref_dict['message'] + "\n Ending program. Please try again")
            print organize_network_ref_dict['exception']
            return
        self.writeToStatusBox(organize_network_ref_dict['message'] + "\n All done! Put link below into Chrome: \n " + self.save_folder+'network_'+self.query_protein_sequence_name+'.html' )

    def checkStartAnalysis(self):
        """
        Checks if   1) we have the path to the maindb.db file
                    2) the entered sequence is >19 characters and is a valid AA sequence
        Once we have, call startAnalysis() to begin analysis

        """
        self.info_label.config(text = "")

        self.query_protein_sequence = self.prot_seq.get("1.0",END)

        self.reference_db_name = self.db_name.get("1.0",END).strip()

        #check for a protein name
        self.query_protein_sequence_name = self.prot_name.get("1.0",END)
        self.query_protein_sequence_name = self.cleanProteinName(self.query_protein_sequence_name)
        if len(self.query_protein_sequence_name) <= 2:
            print self.query_protein_sequence_name
            self.writeToInfoBox("Error! Your sequence name looks too short.")

        # check the prot_seq text box for a  valid protein sequence
        elif len(self.query_protein_sequence) <= 19:
            self.writeToInfoBox("Error! Your sequence looks too short.")
        elif not self.is_protein(self.query_protein_sequence):
            self.writeToInfoBox("This doesn't look like a valid protein sequence. Try again!")
            
        # check we have the home directory file path
        elif not self.home_directory_path:
            self.writeToInfoBox("Error! Select the 'maindb.db' file. ")
        
        # check for db name
        elif len(self.reference_db_name) <= 1:
            self.writeToInfoBox("Error! Your database name looks too short.")

        else:
            # we can begin analysis
            self.writeToInfoBox("Running")
            self.guiPrepareAnalysis()
            

if __name__ == '__main__':
    top = Tk()
    gui = UserInterface(top)
    top.mainloop()