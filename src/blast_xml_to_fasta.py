"""
Julian Paris Morgan
"""
from Bio.Blast import NCBIXML

def blast_xml_to_fasta(input_xml_filelocation, output_fasta_filelocation):
    """
    Takes the absolute file location for a Blastp searches' XML file
    and converts it to a FASTA file that is saved in the output_fasta_filelocation
    """
    result_handle = None
    try:
        result_handle = open(input_xml_filelocation, "r")
    except IOError:
        print "Error: Unable to open file: " + input_xml_filelocation
        return

    #use NCBIXML.parse if multiple results, then use iterator to access each once, or a list to load into memory
    blast_records = list(NCBIXML.parse(result_handle))
    blast_record = blast_records[0]
    save_file = open(output_fasta_filelocation, 'w')
    for alignment in blast_record.alignments:
        for hsp in alignment.hsps:
            save_file.write('>%s|%s\n' % (alignment.accession, alignment.hit_id))
            save_file.write('%s\n' % (hsp.sbjct))

def main():
    """
    Choose input file, automatically save output file, which is a FASTA file, to same location.
    """
    input_xml_filelocation = "/home/imicrobes/uniref90_mmox_blastp.xml"
    output_fasta_filelocation = input_xml_filelocation.split(".")[0] + ".fasta"
    blast_xml_to_fasta(input_xml_filelocation, output_fasta_filelocation)

if __name__ == '__main__':
    main()
 