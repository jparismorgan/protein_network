# Network Visualization

## Synopsis

This project is a tool for analyzing protein homologs to identiy proteins of interest for cloning. There are three main tools you can use.

1. **NetworkBuilder (Main Analysis):** This is the main tool for visual analysis of protein networks. It takes as input the amino acid (AA) sequence of a query protein. It then searches against a UniRef90 database that has been pre-optimized for BLASTp searches using [DIAMOND](https://github.com/bbuchfink/diamond). It takes the top 300 hits from this search and runs an all versus all BLASTp search. Intuitively, this just means that every single protein is compared against every other protein using the BLASTp algorithm with default parameters from DIAMOND. The result of this is a  sequence similarity network (SSN) which we visualization in a HTML file (best viewed in Chrome). This undirected graph uses [Cytoscape.js](http://js.cytoscape.org/) for visualization with [Cola.js](https://github.com/cytoscape/cytoscape.js-cola) as the physics simulation layout. Nodes represent proteins and edges represent the bit-score from the all versus all BLASTp search. Visually, edge lengths are not proportional and instead represent general trends in similarity between two proteins based on the Cola.js laout. To provide better insight into protein associations, the [Markov Cluster Algorithm (MCL)](https://micans.org/mcl/) is used to color proteins in the network into families. We use this [cytoscape.js-markov-cluster](https://github.com/cytoscape/cytoscape.js-markov-cluster) implementation. The MCL can be thought of as similar to PageRank; MCL uses random walks to find densely connected regions of nodes and group them into families. In this graph, we give users the ability to filter based on:
	* Edge percent identity: filters out edges if the percent identity between two proteins is less than the set value
	* Protein length minimum: filters out nodes (proteins) and their connected edges if the length of the protein (in AA's) is less than the set value
	* Name search phrase: filters our nodes and their connected edges if the protein name doesn't contain the search phrase.
		* Word1,Word2 will keep anything with Word1 or Word2 in the name
		* Word1&Word2 will keep anything with Word1 and Word2 in the name
	* Name exclusion phrase: filters our nodes and their connected edges if the protein name contains the search phrase.
		* Word1,Word2 will remove anything with Word1 or Word2 in the name
		* Word1&Word2 will remove anything with Word1 and Word2 in the name
	* Organism search phrase: filters our nodes and their connected edges if the protein organism doesn't contain the search phrase.
		* Word1,Word2 will keep anything with Word1 or Word2 in the name
		* Word1&Word2 will keep anything with Word1 and Word2 in the name

	After using these filters to select a subset of nodes and edges, a user can re-run the physics simulation and MCL algorithm on only the nodes and edges in view. They may also calculate maximally distinct nodes using an in-house algorithm, summarized below:
	* For each node, calculate the sum of all outgoing edges. Only include edges for which both nodes are included in the graph.
	* Within each connected component in the graph, select k nodes with the lowest sum. 
		* k = 20% of total nodes in connected component.

	We then label all nodes with their sums and mark the selected nodes with arrows. At this point, a user may then select nodes for further analysis. By *Shift + Clicking* on a node, they can select it for further analysis. After selecting nodes, a user can export selected nodes as a FASTA file. This can be used in other programs or in NetworkBuilder (Secondary Analysis)
2. **NetworkBuilder (Secondary Analysis):** This tool is accessed from within NetworkBuilder as well. It allows for further analysis on nodes from a FASTA file generated in the following three situations:
	* A FASTA file from the NetworkBuilder (Main Analysis) tool
	* A FASTA file from a past use of the NetworkBuilder (Secondary Analysis) tool
	* A FASTA file from the Automatic Protein Selection tool

	Other FASTA files may work, especially those from UniProtKB, but because of the wide differences between FASTA headers you may run into issues. Please submit a request if you want support for a particular header or would like to work on refactoring & extending this code. Once a user a selected a FASTA file for analysis, we iterate through each protein and retrieve information programmatically based on the protein database:
	* UniRef90 protein: (i.e. it comes from the NetworkBuilder (Main Analysis) tool), we search [UniRef](http://www.uniprot.org/uniref/) to retrieve all of the proteins in each cluster.
	* UniProt protein: These include both Swiss-Prot and TrEMBL proteins. We search [UniProt](http://www.uniprot.org/uniprot/).
	* UniParc protein: This is used to catch some NCBI proteins as well as proteins that didn't catch on UniProt. We search [UniParc](http://www.uniprot.org/uniprot/).
	* NCBI protein: Currently not implemented so no annotation information is provided yet. This includes most proteins from the Automatic Protein Selection tool, though some are caught with the UniParc protein tool.

	Each database provides slightly different information. Once this is complete, we follow the same process as the NetworkBuilder (Main Analysis), performing an all vs all BLASTp search and then visualizing the network.
3. **Automatic Protein Selection:** This tool is separate from the NetworkBuilder tool and is intended to be used as an alternate first step instead of the NetworkBuilder (Main Analysis) tool. It uses a rough algorithm to calculate a selection of maximally distinct proteins from the input of the amino acid (AA) sequence of a query protein. 

## Databases

The UniRef90 database is built "by clustering UniRef100 sequences with 11 or more residues using the CD-HIT algorithm (Li W. and Godzik A., Bioinformatics, 22: 1658-1659, 2006) such that each cluster is composed of sequences that have at least 90% sequence identity to and 80% overlap with the longest sequence (a.k.a. seed sequence) of the cluster." The UniRef100 database "combines identical sequences and sub-fragments with 11 or more residues from any organism into a single UniRef entry, displaying the sequence of a representative protein, the accession numbers of all the merged entries and links to the corresponding UniProtKB and UniParc records"

## Code Example

To start the program, double click on the NetworkBuilder.command file in the NetworkBuilder directory. There are then two stages of analysis you can run:

* The Main Analysis
    1. Enter the name of your protein sequence
        * Any spaces or following characters will be stripped: !, @, #, $, %, ^, &, *, (, ), >, <
    2. Enter the protein sequence. 
        * Only accepts the following characters: ACGTRNDQEHILKMFPSWYV*
    3. Select the location of the NetworkBuilder directory 
        * Click on Google Drive, then click on NetworkBuilder, then click 'Choose'
    4. Click "Begin Analysis'
        * This will start the program, which can take ~10 minutes depending on the protein sequence
        * The status of the analysis will be shown at the bottom in the 'Status Box'
        * Once complete, a blue hyperlink will appear. Click on this link to open the network in Google Chrome
        * This HTML file, and all the associated data for the analysis, will be stored in:
            * /NetworkBuilder/files/year-month-day_protein name_run number
                * Run number means if you run the same protein two times on the same day, the second one will have _02 as a suffix
            * Any folder in /files/ can be deleted without affecting the program    
    5. Viewing the HTML file 
        * To analyze the result, use the filters and protein data to select proteins of interest. After this first analysis, nodes will represent clusters with >90% sequence identity.  After selecting a subset of the proteins, select these nodes and the press 'Export Selected Nodes'. You will then have the option to name and save this file. A typical name for this file is protein name_analysis. You then can go back to the GUI that you used before. There, you can do secondary analysis on these nodes.

* Secondary Analysis
    1. Select the location of the NetworkBuilder directory 
        * Click on Google Drive, then click on NetworkBuilder, then click 'Choose'
    2. Select the file that you downloaded on the HTML page
    3. Choose your anlysis option  
        1. Analysze representative nodes only
            * To just analyze the nodes in the file, and not the UniRef90 clusters, select
        2. Analysze representative nodes and their associated cluster proteins
            * If this is the first analysis after the main program, select this option to retrieve all the sequences of the associated cluster proteins for the nodes you have selected. 
    4. Click "Begin Analysis' and view the HTML file, just as with the Main Analysis

## Motivation

When deciding which novel proteins to clone and test, there is a lack of useful, rapid, extensible, and easy to use tools. The goal of this project was to build an analysis platform that would allow for easy examination of homologs of proteins of interest. 

## Installation

This project is built to be run locally on Mac OS X with Python 2.7 and an updated Chrome build.  

To check your Python build, run:
```
$ python
>>> import sys
>>> print sys.version
```
If you have Python 3, you can:

* Use a virtual environment: [Docs](http://docs.python-guide.org/en/latest/dev/virtualenvs/)
* Downgrade to Python 2.7: [Stack Overflow](https://stackoverflow.com/questions/9246353/how-can-i-downgrade-from-python-3-2-to-2-7)

We use several libraries in this program. If you have a standard built, you should already have the following built in dependencies:

* tkFileDialog
* re
* time
* webbrowser
* os
* subprocess
* xml.etree.ElementTree as ET

You will need to install the following libraries and packages:

* Install pip
    ```
    $ sudo easy_install pip
    ```
* Install requests 2.18.1
    ```
    $ sudo pip install requests
    ``` 
    or 
    ```
    $ sudo easy_install -U requests
    ```

* Install BioPython 1.69
    ```
    $ sudo python2.7 -m pip install biopython
    ```

## Contributors

If you are interested in contributing, please feel free to reach out to Derek Greenfield at derek at imicrobes dot com or Paris Morgan at jparismorgan at gmail dot com 

## License

All rights reserved by Industrial Microbes. If you would like to use this software, please contact Derek Greenfield at derek at imicrobes dot com

