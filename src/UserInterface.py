from Tkinter import Tk, Label, Button, BOTTOM, Frame, Text, RIDGE, END
import tkFileDialog
import re
import main

WIDTH = 600
HEIGHT = 500

class UserInterface:
    def __init__(self, master):
        print self
        print master
        #initialize variables
        self.home_directory_path = None
        self.begin_analysis = False

        #Frame.__init__(self, master)

        #window settings
        master.title("Network Builder")
        master.resizable(width=False, height=False)
        master.configure(bg = "white")
        master.grid()
        master.geometry('{}x{}'.format(WIDTH, HEIGHT))

        #Instructions label
        self.instuctions_label = Label(master, text="Enter the name of you protein sequence")
        self.instuctions_label.pack(pady = 2)
        
        #Text entry box: prot_name
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

        #Instructions label
        self.diamond_label = Label(master, text="Select location of the 'diamond-0.9.9/bin/diamond' executable file")
        self.diamond_label.pack(pady = 2)

        #Get main.db location
        self.get_diamond_file_button = Button(master, text = "Click to navigate", command=self.getDiamondFilePath)
        self.get_diamond_file_button.pack(pady = 2) 
        
        #Label to use for errors & info
        self.info_label = Label(master, text="Follow all steps above and then press 'Begin Analysis'")
        self.info_label.pack(pady = 2)

        #Run button
        self.play_button = Button(master, text = "Begin analysis", command=self.startAnalysis)
        self.play_button.pack(pady = 2) 

        

        #Copyright label
        self.copright_label = Label(master, text="Copyright C 2017 Industrial Microbes, Inc. All Rights Reserved.")
        self.copright_label.pack(side=BOTTOM, pady = 2)
    
    def writeToInfoBox(self, message):
        self.info_label.config(text = message)

    def getHomeDirectoryPath(self):
        """
        Gets the path to the maindb.db directory. Sets it as a variable of user_interface.
        """
        self.home_directory_path = tkFileDialog.askdirectory()
        self.directory_label.config(text =  'Directory: ' + self.home_directory_path)

    def getDiamondFilePath(self):
        """
        Gets the path to the maindb.db file. Sets it as a variable of user_interface.
        """
        self.diamond_file_path = tkFileDialog.askopenfilename()
        self.diamond_label.config(text =  'Diamond file: ' + self.diamond_file_path)

    def is_protein(self,in_str):
        """
        Determine if string is a valid protein sequence; it's valid if it only contains {ACGTRNDQEHILKMFPSWYV} characters.
        """
        if re.findall(r"^[ACGTRNDQEHILKMFPSWYV*]+$", in_str):
            return True
        else:
            return False

    def startAnalysis(self):
        """
        Checks if   1) we have the path to the maindb.db file
                    2) the entered sequence is >19 characters and is a valid AA sequence
        Once we have, self.begin_analysis = True. main.py is running a while loop waiting for this.
        """
        self.info_label.config(text = "")

        self.query_protein_sequence = self.prot_seq.get("1.0",END)

        self.reference_db_name = self.db_name.get("1.0",END)

        #check for a protein name
        self.query_protein_sequence_name = self.prot_name.get("1.0",END)

        if len(self.query_protein_sequence_name) <= 2:
            print self.query_protein_sequence_name
            self.writeToInfoBox("Error! Your sequence name looks too short.")

        #check the prot_seq text box for a  valid protein sequence
        elif len(self.query_protein_sequence) <= 19:
            self.writeToInfoBox("Error! Your sequence looks too short.")
            
        elif not self.is_protein(self.query_protein_sequence):
            self.writeToInfoBox("This doesn't look like a valid protein sequence. Try again!")
            
        #check we have the maindb.db file path
        elif not self.home_directory_path:
            self.writeToInfoBox("Error! Select the 'maindb.db' file. ")
 
        #check for db name
        elif len(self.reference_db_name) <= 1:
            self.writeToInfoBox("Error! Your database name looks too short.")

        #check for the diamond executable
        elif not self.diamond_file_path:
            self.writeToInfoBox("Error! Select the 'diamond-0.9.9/bin/diamond' file file. ")
        
        else:
            #we can begin analysis
            self.writeToInfoBox("Running")
            self.begin_analysis = True
            main.main(self.home_directory_path, self.reference_db_name, self.query_protein_sequence_name, self.query_protein_sequence, self.diamond_file_path)
            return

if __name__ == '__main__':
    top = Tk()
    gui = UserInterface(top)
    top.mainloop()