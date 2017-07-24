import os

import datetime
# path = "~"

import subprocess
 
import glob
import shutil

home_filepath = "/Users/parismorgan/Desktop/iMicrobes/network_builder/"
db_name = 'uniref90'
protein = 'mmox'
diamond_exec = home_filepath + "diamond-0.9.9/bin/diamond"  





def main():
    dest = "/Users/parismorgan/Desktop/iMicrobes/network_builder/files/20Jul17_mmox_01"
    db_protein_path = home_filepath + db_name + "_" + protein
    for file in glob.glob(db_protein_path+'*'):
        shutil.copy(file, dest)
            

    


if __name__ == '__main__':
    main()

# today = date.today()
# cur_date = "%d%b%Y".format(today)
# print cur_date  