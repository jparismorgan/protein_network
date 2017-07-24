from Tkinter import Tk, Label, Button, BOTTOM, Frame, Text, RIDGE, END
import tkFileDialog
import re

WIDTH = 400
HEIGHT = 400

class UserInterface:
    def __init__(self, master):
        print self
        print master
        #initialize variables
        self.maindb_filepath = None
        self.begin_analysis = False

        #Frame.__init__(self, master)

        #window settings
        master.title("Network Builder")
        master.resizable(width=False, height=False)
        master.configure(bg = "white")
        master.grid()
        master.geometry('{}x{}'.format(WIDTH, HEIGHT))

        #Instructions label
        self.instuctions_label = Label(master, text="Enter your sequence and select protein / nucleotide sequence")
        self.instuctions_label.pack(pady = 2)
        
        #Text entry box
        self.text_entry = Text(master, height=10, width=50, bg="#cdc9c9", bd = 1, relief=RIDGE, highlightthickness=0)
        self.text_entry.pack(pady = 2)

        #Get main.db location
        self.get_file_button = Button(master, text = "Select the 'maindb.db' file", command=self.getMainDbPath)
        self.get_file_button.pack(pady = 2) 
        
        #Run button
        self.play_button = Button(master, text = "Begin analysis", command=self.startAnalysis)
        self.play_button.pack(pady = 2) 

        #Label to use for errors & info
        self.info_label = Label(master, text="Info goes here")
        self.info_label.pack(pady = 2)

        #Copyright label
        self.copright_label = Label(master, text="Copyright C 2017 Industrial Microbes, Inc. All Rights Reserved.")
        self.copright_label.pack(side=BOTTOM, pady = 2)
    
    def getMainDbPath(self):
        """
        Gets the path to the maindb.db file. Sets it as a variable of user_interface.
        """
        self.maindb_filepath = tkFileDialog.askopenfilename()

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
        #check the main area text box is a valid protein sequence
        self.query_protein_sequence = self.text_entry.get("1.0",END)
        if len(self.query_protein_sequence) <= 19:
            self.info_label.config(text = "Error! Your sequence looks too short.")

        elif not self.is_protein(self.query_protein_sequence):
            self.info_label.config(text = "This doesn't look like a valid protein sequence. Try again!")
        
        #check we have the maindb.db file path
        elif not self.maindb_filepath:
            self.info_label.config(text = "Error! Select the 'maindb.db' file. ")
        
        #we can begin analysis
        else:
            self.info_label.config(text = "Running")
            self.begin_analysis = True
