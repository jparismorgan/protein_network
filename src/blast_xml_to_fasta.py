"""
Julian Paris Morgan
"""
import re
from Bio.Blast import NCBIXML


def blast_xml_to_fasta(input_xml_location, output_fasta_location):
    """
    1) Takes the absolute file location for a Blastp searches' XML file
    and converts it to a FASTA file that is saved in the output_fasta_filelocation
    2) Saves the first hit to match_protein.js. This is the best match protein to the query.
    """
    # Get the XML file
    result_handle = None
    try:
        result_handle = open(input_xml_location, "r")
    except IOError:
        print "Error: Unable to open file: " + input_xml_location
        return

    # Open the file to save the fasta sequences to
    try:
        converted_fasta_save_file = open(output_fasta_location, 'w')
    except IOError:
        print "Error: Unable to open save file: " + output_fasta_location
        return

    # Open the file to save the best match protein query to
    try:
        match_protein_location = '/'.join(input_xml_location.split('/')[:-1]) + '/match_protein.js'
        print match_protein_location
        match_protein_save_file = open(match_protein_location, 'w')
    except IOError:
        print "Error: Unable to open save file: " + match_protein_location
        return

    # Use NCBIXML.parse if multiple results, then use iterator to access each once, or a list to load into memory
    blast_records = list(NCBIXML.parse(result_handle))
    # Only take the first result. TODO: Check for edge cases here
    blast_record = blast_records[0]
    first = True
    for alignment in blast_record.alignments:
        # for each hit
        for hsp in alignment.hsps:
            #save if first hit
            if first:
                match_protein_save_file.write('var match_protein = {id: "' + alignment.hit_id + '", UniProtKB_accession: "' + alignment.accession + '" }')
                first = False

            converted_fasta_save_file.write('>%s|%s\n' % (alignment.accession, alignment.hit_id))
            converted_fasta_save_file.write('%s\n' % (hsp.sbjct))


def main():
    """
    Choose input file, automatically save output file, which is a FASTA file, to same location.
    """
    input_xml_filelocation = "/Users/parismorgan/Desktop/iMicrobes/network_builder/files/08Aug17_mmox_01/uniref90_mmox.xml"
    output_fasta_filelocation = input_xml_filelocation.split(".")[0] + ".fasta"
    blast_xml_to_fasta(input_xml_filelocation, output_fasta_filelocation)


if __name__ == '__main__':
    main()
