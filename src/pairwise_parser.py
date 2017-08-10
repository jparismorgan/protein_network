"""
Module docstring
"""
import re
import xml.etree.ElementTree as ET
import requests


# list of nodes and edges
nodes = []
edges = {}
match_protein = None


class Edge:
    """
    Edge class
    """

    def __init__(self, id, source, target, percent_id, align_score, align_len, e_value):
        self.id = id
        self.source = source
        self.target = target
        self.percent_id = percent_id
        self.align_score = align_score
        self.align_len = align_len
        self.e_value = e_value


class ClustNode:
    """
    Node class for cluster nodes, which are held within the representative node
    """

    def __init__(self, d):
        for k, v in d.items():
            setattr(self, k, v)


class RepNode:
    """
    Node class for the representative node
    """

    def __init__(self, id_val, d, cluster_members=None):
        self.id = id_val
        self.num_cluster_members = None
        for k, v in d.items():
            setattr(self, k, v)
        self.cluster_members = cluster_members


def unirefAPICall(protein_name):
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
            print "Error!"
        else:
            protein_name = temp[0].replace('"', '').split('=')[-1]
        my_response = requests.get(base_url + protein_name + extension)
        if not my_response.ok:
            print (my_response.status_code)
            # If response code is not ok (200), print the resulting http error code with description. The protein sequence was not in UniProt
            my_response.raise_for_status()

    # get root of the XML response
    root = ET.fromstring(my_response.content)

    # parse the information of the representative member
    rep_member_d = {}
    rep_member = root.find('{http://uniprot.org/uniref}entry').find(
        '{http://uniprot.org/uniref}representativeMember').find('{http://uniprot.org/uniref}dbReference')
    for prop in rep_member.iter():
        if 'value' in prop.attrib:
            rep_member_d[prop.attrib['type'].replace(
                " ", "_")] = prop.attrib['value']
        else:
            rep_member_d[prop.attrib['type'].replace(
                " ", "_")] = prop.attrib['id']

    # initialize the node
    n = RepNode(protein_name, rep_member_d)

    # parse the information of the proteins in the cluster
    cluster_members = []
    # for each cluster member
    for i in root.iter(tag='{http://uniprot.org/uniref}member'):
        member = i.find('{http://uniprot.org/uniref}dbReference')
        member_dict = {}
        # add all properties to the member dict
        # tag = '{http://uniprot.org/uniref}property'
        for prop in member.iter():
            if 'value' in prop.attrib:
                member_dict[prop.attrib['type'].replace(
                    " ", "_")] = prop.attrib['value']
            else:
                member_dict[prop.attrib['type'].replace(
                    " ", "_")] = prop.attrib['id']
        c_node = ClustNode(member_dict)
        cluster_members.append(c_node)


    n.cluster_members = cluster_members
    n.num_cluster_members = len(cluster_members)
    return n

def uniprotAPICall(protein_name):
    """
    Calls the UniProt database with the protein name.
    If no response, the protein is invalid and skip it
    Parse the information about the member
    Return a node with information about the protein
    """
    # API call to UniRef DB
    base_url = "http://www.uniprot.org/uniprot/"
    extension = ".xml"
    my_response = requests.get(base_url + protein_name + extension)
    
    # For successful API call, response code will be 200 (OK)
    if not my_response.ok:
        print protein_name
        return

    # get root of the XML response
    root = ET.fromstring(my_response.content)
    rep_member = root.find('{http://uniprot.org/uniprot}entry')

    # set up dict to put in info
    member_dict = {}

    # Add any properties that have type - id pairings
    for prop in rep_member.iter():
        if 'type' in prop.attrib and 'id' in prop.attrib:
            member_dict[prop.attrib['type'].replace(" ", "_")] = prop.attrib['id']
        # else:
        #     member_dict[prop.attrib['type'].replace(
        #         " ", "_")] = prop.attrib['id']
    
    # Get protein accession. Ex: Q8KM74
    member_dict['UniProtKB_accession'] = rep_member.find('{http://uniprot.org/uniprot}accession').text
    member_dict['id'] = member_dict['UniProtKB_accession']

    # Get specific protein accession. Ex: Q8KM74_METTR
    member_dict['UniProtKB_ID'] =  rep_member.find('{http://uniprot.org/uniprot}name').text

    # Get source organism
    member_dict['source_organism'] =  rep_member.find('{http://uniprot.org/uniprot}organism').find('{http://uniprot.org/uniprot}name').text

    # Get protein existance: http://www.uniprot.org/help/protein_existence
    member_dict['protein_existence'] =  rep_member.find('{http://uniprot.org/uniprot}proteinExistence').attrib['type'] if 'type' in rep_member.find('{http://uniprot.org/uniprot}proteinExistence').attrib else None
    
    # Get protein length
    member_dict['length'] =  int(rep_member.find('{http://uniprot.org/uniprot}sequence').attrib['length']) if 'length' in   rep_member.find('{http://uniprot.org/uniprot}sequence').attrib else None

    #print member_dict
    #name = UniProtKB_accession, UniProtKB_ID (has the _1343),  UniProtKB_accession, id =  UniProtKB_ID, length, protein_name, source_organism, NCBI_taxonomy, UniParc_ID, Pfam,Supfam

    return ClustNode(member_dict)

def parseAllVsAllBlast(blast_allvsall_filepath):
    """"
    Parses the results of a DIAMOND blastp with output format -0
    Creates a list of nodes and edges.
    Edges are unique, such that a-->b does not also exist as b-->a
    """
    try:
        f = open(blast_allvsall_filepath)
    except IOError:
        print "There was an error opening the file: " + blast_allvsall_filepath
        return

    # out_len = open(
    #     '/Users/parismorgan/Desktop/iMicrobes/network_builder/files/das1/histogram_length.txt', 'w')
    # out_percentid = open(
    #     '/Users/parismorgan/Desktop/iMicrobes/network_builder/files/das1/histogram_percentid.txt', 'w')
    # out_evalue = open(
    #     '/Users/parismorgan/Desktop/iMicrobes/network_builder/files/das1/histogram_evalue.txt', 'w')
    # out_score = open(
    #     '/Users/parismorgan/Desktop/iMicrobes/network_builder/files/das1/histogram_score.txt', 'w')


    uniref = False      #is the all vs all a Uniref format

    query = None
    hit = None
    percent_id = None
    align_score = None
    align_len = None
    e_value = None

    for line in f:
        if line == "":
            continue
        line = line.strip()
        if re.search('Query=', line):
            query = line.split('|')[-1]

            if re.search('UniRef', query):
                uniref = True 
            
            if uniref:
                # Call the uniref API to add information to node, then add to node list
                n = unirefAPICall(query)
            else:
                #Call the uniprot API to add information to node, then add node to list
                n = uniprotAPICall(line.split('|')[1])
                
            nodes.append(n)

        elif re.search('>', line):
            if uniref:
                hit = line.split("|")[-1]
            else:
                hit = line.split('|')[1]

        elif re.search('Length=', line):
            align_len = line.split('=')[-1]
            #out_len.write(align_len + '\n')

        elif re.search('Score =', line):
            align_score = line.split()[2]
            e_value = line.split()[-1]
            #out_evalue.write(e_value + '\n')
            #out_score.write(align_score + '\n')

        elif re.search('Identities =', line):
            percent_id = line.split()[3].strip()
            percent_id = percent_id.translate(None, "(),%")
            #out_percentid.write(percent_id + '\n')

            if int(percent_id) > 35:
                # Don't add edge from node to itself, or duplicate edge
                if query != hit:
                    # Don't add self-hits
                    edge_id = ",".join(sorted([query, hit]))
                    if edge_id in edges:
                        # We have found a reciprocal hit between two nodes
                        if edges[edge_id].align_score < align_score:
                            # Create new edge to replace the lower score one
                            e = Edge(edge_id, query, hit, percent_id,
                                    align_score, align_len, e_value)
                            edges[edge_id] = e 
                    else:   
                        # New node1-node2 edge
                        e = Edge(edge_id, query, hit, percent_id,
                                    align_score, align_len, e_value)
                        edges[edge_id] = e
    f.close()
    print len(nodes)
    print len(edges)
    return


def createClustNode(n):
    ret_str = '{data: {'
    for attr, value in n.__dict__.iteritems():
        ret_str += attr + ': "' + value + '", '
    ret_str = ret_str[:-2] + '}}'
    return ret_str


def createRepNode(n):
    ret_str = '{data: {name: "' + n.id + \
        '", num_cluster_members: ' + str(n.num_cluster_members) + ', '
    for attr, value in n.__dict__.iteritems():
        if attr != 'cluster_members' and attr != 'num_cluster_members':
            ret_str += attr + ': "' + str(value) + '", '
    ret_str = ret_str + \
        'cluster_members: [' + ','.join([createClustNode(c)
                                         for c in n.cluster_members]) + '] }},\n'
    return ret_str


def createEdge(e):
    return '\n{data: {source: "' + e.source + '", target: "' + e.target + '", evalue: ' + e.e_value + ', align_len: ' + e.align_len + ', align_score: ' + e.align_score + ', percent_id: ' + e.percent_id + ', id: "' + e.id + '", weight: ' + e.align_score + '},\n},\n'


def createElementsFile(out_filepath):
    """
    Input is an array of Node objects and an array of Edge objects.
    Writes out a a network that is in JSON-esque format that cytoscape.js can read
    Not true JSON: The keys are not strings.
    """
    edge_objects = edges.values()

    # Write node and edge javascript arrays containing node and edge objects, respectively
    with open(out_filepath + "elements.js", "w") as elems_outfile:
        elems_outfile.write('var nodes = [\n')
        # write the nodes
        for n in nodes:
            elems_outfile.write(createRepNode(n))
        elems_outfile.write(']; \n //End of nodes \n\n')
        elems_outfile.write('var edges = [\n')
        # write the edges
        for e in edge_objects:
            elems_outfile.write(createEdge(e))
        elems_outfile.write(']; \n //End of edges \n\n')

    return

def main():
    """
    Parses the results of an all vs all BLAST search
    Creates Node and Edge objects
    Creates an XGMML file for viewing with cytoscape
    """
    f = "/Users/parismorgan/Desktop/iMicrobes/network_builder/files/08Aug17_mmox_02_analysis_06_analysis_01/analysis_temp_allvall"
    parseAllVsAllBlast(f)
    #createElementsFile(
     #   "/Users/parismorgan/Desktop/iMicrobes/network_builder/files/pairwisetest/")


if __name__ == '__main__':
    main()
