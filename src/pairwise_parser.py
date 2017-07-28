import json
import re
import requests
import xml.etree.ElementTree as ET
import subprocess


#list of nodes and edges
nodes = []
edges = []

class Edge:
	"""
	Edge class
	"""
	def __init__(self, source, target, percent_id, align_score, align_len):
		self.id = source + "," + target
		self.source = source
		self.target = target
		self.percent_id = percent_id
		self.align_score = align_score
		self.align_len = align_len

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
	def __init__(self, id_val, d, cluster_members = None):
		self.id = id_val
		self.num_cluster_members = None
		for k, v in d.items():
			setattr(self, k, v)
		self.cluster_members = cluster_members

def uniprotAPICall(protein_name):
	"""
	Calls the UniRef database with the protein name.
	If no response, it is no longer the cluster representative 
		--> Call UniProt, scrape site, and get cluster rep
	Parse the information about the rep member and each of the cluster members
	Return a representative node with information and a list of cluster nodes
	"""
	#API call to UniRef DB
	base_url = "http://www.uniprot.org/uniref/"
	extension = ".xml"
	myResponse = requests.get(base_url + protein_name + extension)

	# For successful API call, response code will be 200 (OK)
	if not myResponse.ok:
		print "Had to search for the real cluster representative"
		# If response code is not ok (200), the cluster is not valid. We will search for the protein in the UniProt DB
		stripped_protein_name = protein_name.split('_')[1] #Assuming a structure of: UniRef90_proteinname_specificid
		url = "http://www.uniprot.org/uniref/?query=uniprot:"+stripped_protein_name+"*&fil=identity:0.9&sort=score"
		myResponse = requests.get(url)
		# For successful API call, response code will be 200 (OK)
		if not myResponse.ok:
			print (myResponse.status_code)
			# If response code is not ok (200), print the resulting http error code with description. The protein sequence was not in UniProt
			myResponse.raise_for_status()

		#We have found the protein in the UniProt DB. We will parse the html page to get the protein that is the cluster representative
		temp = re.findall('id="UniRef90_.*?"', myResponse.content)
		if len(temp) == 0:
			print "Error!"
		else:
			protein_name = temp[0].replace('"', '').split('=')[-1]
		myResponse = requests.get(base_url + protein_name + extension)
		if not myResponse.ok:
			print (myResponse.status_code)
			# If response code is not ok (200), print the resulting http error code with description. The protein sequence was not in UniProt
			myResponse.raise_for_status()

	#get root of the XML response
	root = ET.fromstring(myResponse.content)

	#parse the information of the representative member
	rep_member_d = {}
	rep_member = root.find('{http://uniprot.org/uniref}entry').find('{http://uniprot.org/uniref}representativeMember').find('{http://uniprot.org/uniref}dbReference')
	for prop in rep_member.iter():
		if 'value' in prop.attrib:
			rep_member_d[prop.attrib['type'].replace(" ", "_")] = prop.attrib['value']
		else:
			rep_member_d[prop.attrib['type'].replace(" ", "_")] = prop.attrib['id']

	#initialize the node
	n = RepNode(protein_name, rep_member_d)

	#parse the information of the proteins in the cluster
	cluster_members = []
	#for each cluster member
	for i in root.iter(tag = '{http://uniprot.org/uniref}member'):
		member = i.find('{http://uniprot.org/uniref}dbReference')
		member_dict = {}
		#add all properties to the member dict
		for prop in member.iter(): #tag = '{http://uniprot.org/uniref}property'
			if 'value' in prop.attrib:
				member_dict[prop.attrib['type'].replace(" ", "_")] = prop.attrib['value']
			else:
				member_dict[prop.attrib['type'].replace(" ", "_")] = prop.attrib['id']
		c_node = ClustNode(member_dict)
		cluster_members.append(c_node)

	n.cluster_members = cluster_members
	n.num_cluster_members = len(cluster_members)
	return n

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

	#build a dictionary with query: [hits] to prevent duplicates
	existing_edges = dict()

	query = None
	hit = None
	percent_id = None
	align_score = None
	align_len = None

	for line in f:
		if line == "":
			continue
		line = line.strip()
		if re.search('Query=', line):			
			query = line.split('|')[-1]
			#Call the uniprot API to add information to node, then add to node list
			n = uniprotAPICall(query)
			nodes.append(n)

		elif re.search('>', line):
			hit = line.split("|")[-1]

		elif re.search('Length=', line):
			align_len = line.split('=')[-1]

		elif re.search('Score =', line):
			align_score = line.split()[2]

		elif re.search('Identities =', line):
			percent_id = line.split()[3].strip()
			percent_id = percent_id.translate(None, "(),%")
			if int(percent_id) > 45:
				#Don't add edge from node to itself, or duplicate edge
				try:
					query in existing_edges[hit]
				except:
					if query != hit:
						#Add a new edge
						#if query in subset and hit in subset:
						e = Edge(query, hit, percent_id, align_score, align_len)
						edges.append(e)
						#Add the edge to the edges dictionary to filter duplicates
						if query in existing_edges:
							existing_edges[query].append(hit)
						else:
							existing_edges[query] = [hit]

	f.close()
	print len(nodes)
	print len(edges)
	return	

def createClustNode(n):
	ret_str = '{data: {' 
	for attr, value in n.__dict__.iteritems():
		ret_str += attr+': "'+value+'", '
	ret_str = ret_str[:-2] + '}}'
	return ret_str

def createRepNode(n):
	ret_str = '{data: {name: "'+n.id+'", num_cluster_members: '+str(n.num_cluster_members)+', ' 
	for attr, value in n.__dict__.iteritems():
		if attr != 'cluster_members' and attr != 'num_cluster_members':
			ret_str += attr+': "'+str(value)+'", '	
	ret_str = ret_str + 'cluster_members: ['+ ','.join([createClustNode(c) for c in n.cluster_members]) +'] }},\n'
	return ret_str
	
def createEdge(e):
    return '\n{data: {source: "'+e.source+'", target: "'+e.target+'", align_len: '+e.align_len+', align_score: '+e.align_score+', percent_id: '+e.percent_id+', id: "'+e.id+'", weight: '+e.align_score+'},\n},\n'

def createElementsFile(out_filepath):
	"""
	Input is an array of Node objects and an array of Edge objects.
	Writes out a a network that is in JSON-esque format that cytoscape.js can read
	Not true JSON: The keys are not strings.
	"""
	#Write the network to a text file for debugging
	
	with open(out_filepath + "elements.js", "w") as elems_outfile:
		elems_outfile.write('var nodes = [\n')
		for n in nodes:
			elems_outfile.write(createRepNode(n))
		elems_outfile.write(']; \n //End of nodes \n\n')
		elems_outfile.write('var edges = [\n')
		for e in edges:
			elems_outfile.write(createEdge(e))
		elems_outfile.write(']; \n //End of edges \n\n')
	
	

	#Write the network straight to network.js to be viewed locally in an html page.
	#Delete everything in network.js up to the string "\\End of protein elements."
	#Then write the network to the file.
	# with open(out_filepath + 'network.js', 'r') as infile, open(out_filepath +'network_temp.js', 'a') as outfile:
	# 	# Read the file line by line...
	# 	for line in iter(infile.readline, ''):
	# 		# until we have a match.
	# 		if "//End of protein elements" in line:
	# 			# Read the rest of the input in one go and write it
	# 			# to the output. If you file is really big you might
	# 			# run out of memory doing this and have to break it
	# 			# into chunks.
	# 			outfile.write(infile.read())

	# 			# Our work here is done, quit the loop.
	# 			break
	
	# if raw_input("Press y after inspecting the temporary network_temp.js file") == 'y':
	# 	subprocess.call("mv "+out_filepath+"network_temp.js "+out_filepath+"network.js", shell=True)
	return

def main():
	"""
	Parses the results of an all vs all BLAST search
	Creates Node and Edge objects
	Creates an XGMML file for viewing with cytoscape
	"""
	parseAllVsAllBlast("/Users/parismorgan/Desktop/iMicrobes/network_builder/files/24Jul17_mmox_01/uniref90_mmox_allvall")
	createElementsFile("/Users/parismorgan/Desktop/iMicrobes/network_builder/web/")
	 
if __name__ == '__main__':
	main()