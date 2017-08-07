def convertFastaToJs(filepath, db_name, protein):
    with open(filepath + db_name + "_" + protein + ".fasta", "r") as fasta_file, open(filepath + "fasta_js_map.js", "w") as js_file:
        id = ""
        seq = ""
        js_file.write('var uniref_protein_map = [\n')
        for l in fasta_file:
            l = l.strip()
            if l[0] == '>':
                id = l[1:].split('|')[0]
            else:
                seq = l
                js_file.write('{id: "'+id+'", sequence: "'+seq+'"},\n')
        js_file.write(']')
    return

def main():
    filepath = "/Users/parismorgan/Desktop/iMicrobes/network_builder/files/31Jul17_mmox_01/"
    db_name = "uniref90"
    protein = "mmox"
    convertFastaToJs(filepath, db_name, protein)

if __name__ == '__main__':
    main()