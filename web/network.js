var cy;             //graph object
var layout;         //layout object
var pid = 85;       //edge percent identity cutoff
var plen = 180;     //node protein length cutoff
var pname = "";     //node name substring phrase
var pnot = "";      //node name substring exclusion phrase

var params = {      //parameters for the layout
        name: 'cola',
        pixelRatio: 1, //performance optimization
        hideEdgesOnViewport: true, //performance
        textureOnViewport: true, //performance optimization
        maxSimulationTime: 2000,
        //nodeSpacing: 1,// function( node ){ return 1;  },
        randomize: false,
        // edgeLength: function( edge ){
        //     var len = parseInt(edge.data('weight')); 
        //     return 1 / (1000*len) ; 
        // },
        handleDisconnected: true,
        avoidOverlap: true,
        infinite:false,
    };


var mcl_options = { //options for the MCL algorithm
    expandFactor: 2,        // affects time of computation and cluster granularity to some extent: M * M
    inflateFactor: 2,       // affects cluster granularity (the greater the value, the more clusters): M(i,j) / E(j)
    multFactor: 1,          // optional self loops for each node. Use a neutral value to improve cluster computations.
    maxIterations: 50,      // maximum number of iterations of the MCL algorithm in a single run
    attributes: [           // attributes/features used to group nodes, ie. similarity values between nodes
        function(edge) {
            return edge.data('weight');
        },
        function(edge) {
            return edge.data('percent_id');
        }
     ]
};

/**
 * Runs the Markov Cluster Agorithm on the cy graph
 * @returns {object} returns array of Collections, each being a single cluster
 * Assigns colors to all nodes in clusters
 */
function mcl(){
    // Run Markov cluster on graph
    var clusters = cy.elements().markovCluster( mcl_options );
    colors = ["#79383d","#6eb94a","#c50e1f","#8ef3b7","#4afaec","#f4e960","#83a9b9","#2183de","#9867c","#d8a025","#6db694","#444b90","#41f48a","#12e6de","#fbfc7d","#342102","#20ecbe","#d12ff8","#c70ae6","#5c48de","#e503ea","#20009e","#c6b908","#675558","#d1f426","#5bf727","#f9acf1","#1b1510","#6c293","#1d9051","#8bfb6e","#812bb1","#b2f901","#b45eb4","#551ca4","#68eefe","#39dee6","#616a70","#ae6da6","#e57f12","#5fd922","#d0037a","#7e05cd","#2ee926","#5426d9","#f15f92","#4ebd29","#ea2d1b","#4f35e1","#670ba7","#9aa076","#6596ce","#1625b0","#982f0","#9f27c","#e09128","#fd058e","#36fcbf","#346283","#8b705e","#5f477f","#a3a887","#17e8","#834747","#f25ed3","#5daca3","#f707a1",]
    colors2 =["#000000","#FFFF00","#1CE6FF","#FF34FF","#FF4A46","#008941","#006FA6","#A30059","#FFDBE5","#7A4900","#0000A6","#63FFAC","#B79762","#004D43","#8FB0FF","#997D87","#5A0007","#809693","#FEFFE6","#1B4400","#4FC601","#3B5DFF","#4A3B53","#FF2F80","#61615A","#BA0900","#6B7900","#00C2A0","#FFAA92","#FF90C9","#B903AA","#D16100","#DDEFFF","#000035","#7B4F4B","#A1C299","#300018","#0AA6D8","#013349","#00846F","#372101","#FFB500","#C2FFED","#A079BF","#CC0744","#C0B9B2","#C2FF99","#001E09","#00489C","#6F0062","#0CBD66","#EEC3FF","#456D75","#B77B68","#7A87A1","#788D66","#885578","#FAD09F","#FF8A9A","#D157A0","#BEC459","#456648","#0086ED","#886F4C","#34362D","#B4A8BD","#00A6AA","#452C2C","#636375","#A3C8C9","#FF913F","#938A81","#575329","#00FECF","#B05B6F","#8CD0FF","#3B9700","#04F757","#C8A1A1","#1E6E00","#7900D7","#A77500","#6367A9","#A05837","#6B002C","#772600","#D790FF","#9B9700","#549E79","#FFF69F","#201625","#72418F","#BC23FF","#99ADC0","#3A2465","#922329","#5B4534","#FDE8DC","#404E55","#0089A3","#CB7E98","#A4E804","#324E72","#6A3A4C","#83AB58","#001C1E","#D1F7CE","#004B28","#C8D0F6","#A3A489","#806C66","#222800","#BF5650","#E83000","#66796D","#DA007C","#FF1A59","#8ADBB4","#1E0200","#5B4E51","#C895C5","#320033","#FF6832","#66E1D3","#CFCDAC","#D0AC94","#7ED379","#012C58","#7A7BFF","#D68E01","#353339","#78AFA1","#FEB2C6","#75797C","#837393","#943A4D","#B5F4FF","#D2DCD5","#9556BD","#6A714A","#001325","#02525F","#0AA3F7","#E98176","#DBD5DD","#5EBCD1","#3D4F44","#7E6405","#02684E","#962B75","#8D8546","#9695C5","#E773CE","#D86A78","#3E89BE","#CA834E","#518A87","#5B113C","#55813B","#E704C4","#00005F","#A97399","#4B8160","#59738A","#FF5DA7","#F7C9BF","#643127","#513A01","#6B94AA","#51A058","#A45B02","#1D1702","#E20027","#E7AB63","#4C6001","#9C6966","#64547B","#97979E","#006A66","#391406","#F4D749","#0045D2","#006C31","#DDB6D0","#7C6571","#9FB2A4","#00D891","#15A08A","#BC65E9","#FFFFFE","#C6DC99","#203B3C","#671190","#6B3A64","#F5E1FF","#FFA0F2","#CCAA35","#374527","#8BB400","#797868","#C6005A","#3B000A","#C86240","#29607C","#402334","#7D5A44","#CCB87C","#B88183","#AA5199","#B5D6C3","#A38469","#9F94F0","#A74571","#B894A6","#71BB8C","#00B433","#789EC9","#6D80BA","#953F00","#5EFF03","#E4FFFC","#1BE177","#BCB1E5","#76912F","#003109","#0060CD","#D20096","#895563","#29201D","#5B3213","#A76F42","#89412E","#1A3A2A","#494B5A","#A88C85","#F4ABAA","#A3F3AB","#00C6C8","#EA8B66","#958A9F","#BDC9D2","#9FA064","#BE4700","#658188","#83A485","#453C23","#47675D","#3A3F00","#061203","#DFFB71","#868E7E","#98D058","#6C8F7D","#D7BFC2","#3C3E6E","#D83D66","#2F5D9B","#6C5E46","#D25B88","#5B656C","#00B57F","#545C46","#866097","#365D25","#252F99","#00CCFF","#674E60","#FC009C","#92896B"]

    //colors = []
    // Assign random colors to each cluster!
    for (var c = 0; c < clusters.length; c++) {        
        if (colors2.length !== 0){
            clusters[c].style( 'background-color', colors2.shift());    
        }
        else{
            color = '#' + Math.floor(Math.random()*16777215).toString(16);
            clusters[c].style( 'background-color', color );
            //colors.push(color);
        }
    }
    return clusters
};

var removed_elems;
/**
 * Get nodes and edges to remove that don't match the pname search
 * @param {string} search_term - phrase to search for in cy
 * @param {string} search_field - field of node to search for in cy
 * @param {bool} exclude_bool - set to true to exclude search_term from results
 * @return {object} selector_matches - elements to remove
 * Term1       --> Keep anything with Term1 in name
 * Term1,Term2 --> Keep anything with Term1 or Term2 in the name
 * Term1 Term2 --> Keep anything with Term1 or Term2 in the name
 * Term1&Term2 --> Keep anything with Term1 and Term2 in the name
 * Returns a collection of nodes and edges to remove
 * selector documentation: http://js.cytoscape.org/#selectors
 */
function selectElemsFromCy(search_term, search_field, exclude_bool){
    var search_term_list = null //list to create longer selector term
    
    var selector_pre //string with '!' for use in selector when excluding or '' when not excluding
    if (exclude_bool == true){
        //we want to exclude the search_term from the results
        selector_pre = ""
    } 
    else{ 
        //we want to keep the search_term in the results
        selector_pre = "!"
    }
    
    //remove leading and trailing whitespace
    search_term = search_term.trim()

    //selector phrase to search the cy graph for
    var selector = "";
    
    //check for an 'and' command, specified with an '&'
    search_term_list = search_term.split('&');
    if (search_term_list.length > 1){
        //for each of multiple search terms
        for (var n in search_term_list){
            //node[selector1],node[selector2] --> node[selector1] OR node[selector2] 
            selector += 'node['+search_field+selector_pre+'@*="' + search_term_list[n] + '"],'; 
        }
        //remove trailing comma
        selector = selector.replace(/(^,)|(,$)/g, "")
    }
    //check for an 'or' command, specified with an comma or a space
    else{ 
        //split on comma
        search_term_list = search_term.split(" ")
        //if no comma
        if (search_term_list.length <= 1){
            //split on space
            search_term_list = search_term.split(" ")
        } 
        //if there are multiple search terms
        if (search_term_list.length > 1){
            selector += "node";
            //treat each phrase in the pname search as separate
            for (var n in search_term_list){
                selector += '['+search_field+' '+selector_pre+'@*="' + search_term_list[n] + '"]'; 
            }
        }
        //there are not multiple search terms, just search for single term 
        else{
            selector += 'node['+search_field+' '+selector_pre+'@*="' + search_term + '"]'; 
        }
    } 
    console.log(selector)
    //get the nodes to remove
    var selector_matches = cy.elements(selector);
    console.log(selector_matches)
    //remove these nodes and their connected edges. add all to removed_elems array
    console.log(typeof selector_matches)
    return selector_matches.union(selector_matches.connectedEdges())

}

/** 
 * Updates the network graph according to cutoffs
 * Gets several values from html by ID
 * protein percent identity (pid), protein length (plen), 
 * protein name search phrase (pname), protein organism search phrase (porg)
 * name phrase to exclude (pnot)  
 */
function updateCutoff(){

    //get the pid, plen, and pname
    pid = document.getElementById('pid').value;
    plen = document.getElementById('plen').value;
    pname = document.getElementById('pname').value;
    porg = document.getElementById('porg').value;
    pnot = document.getElementById('pnot').value;

    if (removed_elems === undefined){
        removed_elems = cy.collection();
    }

   
    //restore previously removed elements
    if (removed_elems){
        removed_elems.restore();
    }
    removed_elems = cy.collection();
 
    //remove nodes by pname
    if (pname !== "" && pname !== undefined){
        removed_elems = removed_elems.union(selectElemsFromCy(pname,'protein_name',false));
    }

     //remove nodes by porg
    if (porg !== "" && porg !== undefined){
        removed_elems = removed_elems.union(selectElemsFromCy(porg,'source_organism',false));
    }

    //remove nodes by pnot
    if (pnot !== "" && pnot !== undefined){
        removed_elems = removed_elems.union(selectElemsFromCy(pnot,'protein_name',true));
    }

    //remove nodes by plen
    var rem_plen = cy.elements("node[length < " + plen + "]");
    removed_elems = removed_elems.union(rem_plen.union(rem_plen.connectedEdges()));

    //remove edges by pid
    removed_elems = removed_elems.union(cy.elements("edge[percent_id < " + pid+ "]"));
    
    //actually remove elements from the graph
    cy.remove(removed_elems)

    //update html span's
    document.getElementById("pname-label").innerHTML = "Name search term: " + pname;
    document.getElementById("pnot-label").innerHTML = "Exclusion term: " + pnot;
    document.getElementById("porg-label").innerHTML = "Organism search term: " + porg;
    document.getElementById("plen-label").innerHTML = plen;
    document.getElementById("pid-label").innerHTML = pid;
}

/**
 * @param {*} pid_cutoff - percent id cutoff text
 * Updates the text of the pid-label in network.html
 */
function updatePidLabel(pid_cutoff){

    document.getElementById("pid-label").innerHTML = pid_cutoff;
    document.getElementById("pid").value = pid_cutoff; 
}

/**
 * @param {*} plen_cutoff - protein length cutoff text
 * Updates the text of the plen-label in network.html
 */
function updatePlenLabel(plen_cutoff){
    document.getElementById("plen-label").innerHTML = plen_cutoff;
    document.getElementById("plen").value = plen_cutoff
}

/** 
 * @param {int} pid_cutoff - percent id cutoff
 * @param {int} plen_cutoff - protein length cutoff
 * @return {object} all elems - contains all_elems['graph_elems'] and all_elems['exclude_elems'];
 * Returns an array of edges and nodes matching cutoffs
 * Input is the pid and plen cutoffs
 * Edges meet the protein percent identity (pid) cutoff 
 * Nodes meet protein length (plen) cutoff 
 **/
function selectElements(pid_cutoff, plen_cutoff){
    
    var graph_elems = [];       //elements that pass criteria
    var exclude_elems = [];     //elements the fail criteria
    
    var node_set = new Set();   //set of nodes to make sure edges' source & destination nodes are in graph
    for(i in nodes){
        n = nodes[i];
        if (n['data']['length'] > plen_cutoff){
            //if protein length above threshold add to graph_elems
            graph_elems.push(n);
            node_set.add(n['data']['id'])
        } else{
            //if protein length not above threshold add to exclude_elems
            exclude_elems.push(n);
        }
    }
    for (i in edges){
        e = edges[i];
        //check if the edge percent id (i.e. how similar the two proteins are) is greater than cutoff
        if (e['data']['percent_id'] > pid_cutoff){
            //if edge length above threshold 
            var edge_parents = e['data']['id'].split(',');
            if (node_set.has(edge_parents[0]) && node_set.has(edge_parents[1])){
                //if edge source and target nodes are present add edge to graph_elems
                graph_elems.push(e);
            }
        }
        else{
            //add bad edge to exclude_elems
            exclude_elems.push(e);
        }
    }
    //return object to parse
    return {graph_elems: graph_elems, exclude_elems:exclude_elems};
};

var graph_elems     //elems to have in graph layout 
var exclude_elems   //elems to not have in graph layout
var firstRun = true //variable to re-run buildGraph() on the first initialization (cytoscape is wierd with it's layout engine)
var selected_elems = null //elems to put in the selection-checkbox area
/**
 * Builds the cytoscape graph. 
 * Used on initialization with the global pid, plen, and pname phrases.
 * Takes these three variables to get matching nodes and edges via selectElements()
 * Then deletes the past cy graph and creates a new one
 * Adds in nodes and edges that didn't meet critera after creation so they can be seen
 * Binds the node click and edge click functions to cy
 */    
function buildGraph(){
    
    //set variables from global
    var pid_cutoff = pid;
    var plen_cutoff = plen;

    //if not the first time creating cy
    if (cy === undefined){
        //call SelectElements to parse the pairwise_parser.py output
        all_elems =  selectElements(pid_cutoff, plen_cutoff);
        //elements to include in the graph
        graph_elems = all_elems['graph_elems'];
        //elements to exclude in the graph, but to add in after creation
        exclude_elems = all_elems['exclude_elems'];
    } else{
        //update the graph with settings
        updateCutoff();
        //elements in the new graph are in cy
        graph_elems = cy.elements();
        //elements to exclude are in removed_elems
        exclude_elems = removed_elems;
    }

    //destroy previous graph
    if ( cy !== undefined) { cy.destroy(); }      
    
    //create new cy graph. Don't add elems yet (b/c we add two different types of element collectisons)
    //On initialization we add raw objects from nodes and edges arrays. On subsequent builds we add a cytoscape collection from updateGraph()
    new_cy = cytoscape({
        container: document.getElementById('cy'),
        zoom: .3,
        minZoom: .1,
        maxZoom: 1.2,
        style: [{
        selector: 'node',
            style: {
            // 'content': 'data(name)',
            'width': 'mapData(num_cluster_members, 0, 120, 40,  120)',  //size gradient by # clust membs 
            'height': 'mapData(num_cluster_members, 0, 120, 40, 120)', 
            }
        },
        {
        selector: 'edge',
            css: {
                'width': 5,
                'line-color': "#A9A9A9",
            }
        },
    ],
    });
    //add elements to the graph
    new_cy.add(graph_elems)
    
    //create the layout
    layout = new_cy.layout(params);
    layout.run();
    
    //reassign new_cy to permanent variable
    cy = new_cy;

     //run the MCL algorithm to color nodes (relies on having cy to operate)
    mcl();

    //when cy is loaded
    cy.ready(function(event){
            //add in nodes and edges that didn't meet cutoff
            cy.add(exclude_elems);
            //update labels
            updatePidLabel(pid_cutoff);
            updatePlenLabel(plen_cutoff);
            //update the graph cutoff (just in case, but does catch some wierd edge cases)
            updateCutoff();
            //hide the loading icon
        });

    //initialize collection
    if (firstRun === true){
        console.log("first run")
        firstRun = false
        selected_elems = cy.collection()
    }
    
    var past_node = null;
    var node_neighbors = null;
    /**
     * Displays information about the node clicked on or hovering over
     */
    function displayNodeInfo(e){
        // var len = colors.length, text = "[";
        // for (var i = 0; i < len; i++) {            
        //     text += '"'+ colors[i] + '",'
        // }
        // text += ']'
        // document.getElementById("info").innerHTML = text;
        
        var ele = e.target;
        //console.log(ele);
        //Update info box
        info_text = ""
        info_text += 'protein_name: ' + ele.data('protein_name') + '<br>'
        info_text += 'source_organism: ' + ele.data('source_organism') + '<br>'
        info_text += 'length: ' + ele.data('length') +  '<br>'
        info_text += 'NCBI_taxonomy: ' + ele.data('NCBI_taxonomy') + '<br>'
        info_text += 'UniProtKB_accession: <a href="http://www.uniprot.org/uniprot/' + ele.data('UniProtKB_accession') +'" target="_blank">' +ele.data('UniProtKB_accession')+'</a><br>'
        info_text += 'Uniparc: <a href="http://www.uniprot.org/uniparc/' + ele.data('UniParc_ID') +'" target="_blank">' +ele.data('UniParc_ID')+'</a><br>'
        info_text += 'NCBI_taxonomy: <a href="https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id=' + ele.data('NCBI_taxonomy') +'" target="_blank">' +ele.data('NCBI_taxonomy')+'</a><br>'
        info_text += 'num_cluster_members: ' + ele.data('num_cluster_members') + '<br>'
        
        //Protein name: " + ele.data('id') + "<br> Num Cluster Members: " + ele.data('num_cluster_members');
        document.getElementById("info-text").innerHTML = info_text;
        
        //Color neighboring nodes red
        if (node_neighbors){
        node_neighbors.animate({
            style: { lineColor: "#A9A9A9"}
        });}
        node_neighbors =  ele.connectedEdges()
        node_neighbors.animate({
            style: { lineColor: 'red' }
        });


        //Color target node
        if (past_node && past_node !== ele){
            past_node.animate({
                style: {
                'border-width': 0,
                }
            });
        }
        ele.animate({
            style: {
                'border-width': 10,
                'border-color': 'red',
            }
        })
        past_node = ele;
    }
    
    
    //console.log(selected_elems)
    /**
     * Displays node info on click
     * Adds element to selected elements if shift key is held down
     */
    cy.$('node').on('click', function(e){
        if (shifted){
            //add element to selected elems
            selected_elems = selected_elems.add(e.target)
            //update the checkbox to include it
            //get the <ul> list
            var ul = document.getElementById("selection-area")     
            //create <li> element
            var li = document.createElement('li');
            //add data to li
            var ele = e.target;
            li.innerHTML = ele.data('protein_name') + " " + ele.data('UniProtKB_accession')
            //append li to ul
            ul.appendChild(li)
        }
        console.log(selected_elems)

        displayNodeInfo(e);
    });
    
    //on hover
    cy.$('node').on('mouseover', function(e){
        displayNodeInfo(e);
    });

    //on edge click function
    cy.$('edge').on('click', function(e){
        var ele = e.target;
        console.log(ele);
        var info_text = ""
        for (var key in ele.data()) {
            if (ele.data().hasOwnProperty(key)) {
                info_text = info_text.concat(key + " -> " + ele.data()[key] + "<br>");
                }
        }   
        //Update info box
        document.getElementById("info-text").innerHTML = info_text;
    });

    //
    
}
//build graph initially
buildGraph();

var shifted = null
$(document).on('keyup keydown', function(e){
    shifted = e.shiftKey
} );

