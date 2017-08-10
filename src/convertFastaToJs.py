"""
Takes in a fasta file and creates a javascript variable containing protein accession number --> protein sequence objects
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
        js_file.write('var uniref_protein_map = [\n')
        for l in fasta_file:
            l = l.strip()
            if l[0] == '>':
                id = l[1:].split('|')[0]
            else:
                seq = l
                js_file.write('{id: "' + id + '", sequence: "' + seq + '"},\n')
        js_file.write(']')
    return


def main():
    save_folder_protein = "/Users/parismorgan/Desktop/iMicrobes/network_builder/files/31Jul17_mmox_01/mmox"
    save_folder = "/Users/parismorgan/Desktop/iMicrobes/network_builder/files/31Jul17_mmox_01/"
    convertFastaToJs(save_folder_protein, save_folder)

if __name__ == '__main__':
    main()
