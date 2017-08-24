# Network Visualization

## Synopsis

This project is a tool for analyzing protein homologs to identiy proteins of interest for cloning.
It takes a query protein and builds a sequence similarity network (SSN) based on all versus all BLASTp bit-scores as the weighted edges. 
It allows for multiple rounds of analysis on the created network, drilling down on target proteins and providing annotated information.

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

