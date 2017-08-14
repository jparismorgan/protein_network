"""
Takes in a fasta file and creates a javascript variable containing protein accession number --> protein sequence objects
----------------------------------------------------------------
Industrial Microbes C 2017 All Rights Reserved
Contact: J Paris Morgan (jparismorgan@gmail.com) or Derek Greenfield (derek@imicrobes.com)
"""
def convertFastaToJs(save_folder_protein, save_folder):
    """
    Takes in a fasta file and creates a javascript variable containing protein accession number --> protein sequence objects
    The accession number is based on however the fasta file is formatted
    I.e. >P22869|UniRef90_P22869 --> P22869 is the accession number
    """
    with open(save_folder_protein + ".fasta", "r") as fasta_file, open(save_folder + "fasta_js_map.js", "w") as js_file:
        id = ""
        seq = ""
        js_file.write('var uniref_protein_map = [\n {id: "", sequence:"')
        for l in fasta_file:
            l = l.strip()
            if l[0] == '>':
                js_file.write('"},\n')
                split_line = l[1:].split('|')
                if len(split_line) == 1:
                    id = split_line[0].split(" ")[0]
                else:
                    id = split_line[0] if len(split_line[0]) >= 3 else split_line[1].split(' ')[0]
                js_file.write('{id: "' + id + '", sequence: "')
            else:
                js_file.write(l.strip())
        js_file.write('"}]')
    return


def main():
    save_folder_protein = "/Users/parismorgan/Desktop/iMicrobes/network_builder/files/11Aug17_mmox_01_analysis_01/mmox_nodes_temp"
    save_folder = "/Users/parismorgan/Desktop/iMicrobes/network_builder/files/11Aug17_mmox_01_analysis_01/"
    convertFastaToJs(save_folder_protein, save_folder)

if __name__ == '__main__':
    main()
