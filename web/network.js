var cy;         //graph object
var layout;     //layout object
var pid = 85;   //edge percent identity cutoff
var plen = 400;  //node protein length cutoff
var pname = ""; //node name substring phrase
var pnot = "";

var params = {  //parameters for the layout
        name: 'cola',
        pixelRatio: 1, //performance optimization
        hideEdgesOnViewport: true, //performance
        textureOnViewport: true, //performance optimization
        maxSimulationTime: 5000,
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
    maxIterations: 10,      // maximum number of iterations of the MCL algorithm in a single run
    attributes: [           // attributes/features used to group nodes, ie. similarity values between nodes
        function(edge) {
            return edge.data('weight');
        },
        function(edge) {
            return edge.data('percent_id');
        }
     ]
};

function mcl(){
    // Run Markov cluster on graph
    var clusters = cy.elements().markovCluster( mcl_options );
    colors = ["#79383d","#6eb94a","#c50e1f","#8ef3b7","#4afaec","#f4e960","#83a9b9","#2183de","#9867c","#d8a025","#6db694","#444b90","#41f48a","#12e6de","#fbfc7d","#342102","#20ecbe","#d12ff8","#c70ae6","#5c48de","#e503ea","#20009e","#c6b908","#675558","#d1f426","#5bf727","#f9acf1","#1b1510","#6c293","#1d9051","#8bfb6e","#812bb1","#b2f901","#b45eb4","#551ca4","#68eefe","#39dee6","#616a70","#ae6da6","#e57f12","#5fd922","#d0037a","#7e05cd","#2ee926","#5426d9","#f15f92","#4ebd29","#ea2d1b","#4f35e1","#670ba7","#9aa076","#6596ce","#1625b0","#982f0","#9f27c","#e09128","#fd058e","#36fcbf","#346283","#8b705e","#5f477f","#a3a887","#17e8","#834747","#f25ed3","#5daca3","#f707a1",]
    //colors = []
    // Assign random colors to each cluster!
    for (var c = 0; c < clusters.length; c++) {        
        if (colors.length !== 0){
            clusters[c].style( 'background-color', colors.shift());    
        }
        else{
            color = '#' + Math.floor(Math.random()*16777215).toString(16);
            clusters[c].style( 'background-color', color );
            //colors.push(color);
        }
    }
};

var removed_elems;

var past_pid = pid;
var past_plen = plen;
var past_pname = "";
var past_pnot = "";
function updateCutoff(){
    /** 
     * Updates the network graph according to cutoffs
     * Uses protein percent identity (pid), protein length (plen), protein name substring (pname), and phrase not in protein's name (pnot)  
     * These are stored in network.html forms and buttons.
     */
    
    //get the pid, plen, and pname
    pid = document.getElementById('pid').value;
    plen = document.getElementById('plen').value;
    pname = document.getElementById('pname').value;
    pnot = document.getElementById('pnot').value;

    if (removed_elems === undefined){
        removed_elems = cy.collection();
    }

    if ( past_pid < pid || past_plen < plen || past_pname !== pname || past_pnot !== pnot){
        //restore previously removed elements
        if (removed_elems){
            removed_elems.restore();
        }
        removed_elems = cy.collection();
    }
    
    //selector documentation: http://js.cytoscape.org/#selectors
    //remove nodes by pname
    if (pname !== "" && pname !== undefined){
        var pnames = pname.split(' ');
        var selector_pname = "";
        for (var n in pnames){
            selector_pname += 'node[protein_name !@*="' + pnames[n] + '"],';
        }
        selector_pname = selector_pname.replace(/(^,)|(,$)/g, "")
        var rem_pname = cy.elements(selector_pname);
        removed_elems = removed_elems.union(rem_pname.union(rem_pname.connectedEdges()));
    }

    //remove nodes by pnot
    if (pnot !== "" && pnot !== undefined){
        var pnots = pnot.split(' ');
        var selector_pnot = "";
        for (var n in pnots){
            selector_pnot += 'node[protein_name @*="' + pnots[n] + '"],';
        }
        selector_pnot = selector_pnot.replace(/(^,)|(,$)/g, "")
        var rem_pnot = cy.elements(selector_pnot);
        removed_elems = removed_elems.union(rem_pname.union(rem_pname.connectedEdges()));
    }

    //remove nodes by plen
    var rem_plen = cy.elements("node[length < " + plen + "]");
    removed_elems = removed_elems.union(rem_plen.union(rem_plen.connectedEdges()));

    //remove edges by pid
    removed_elems = removed_elems.union(cy.elements("edge[percent_id < " + pid+ "]"));
    
    cy.remove(removed_elems)

    //update html span's
    document.getElementById("pname-label").innerHTML = "Search term: " + pname;
    document.getElementById("pnot-label").innerHTML = "Exclusion term: " + pnot;
    document.getElementById("plen-label").innerHTML = plen;
    document.getElementById("pid-label").innerHTML = pid;
    
    past_pid = pid
    past_plen = plen
    past_pname = pname
    past_pnot = pnot
}

function updatePidLabel(pid_cutoff){
    /**
     * Updates the text of the pid-label in network.html
     */
    document.getElementById("pid-label").innerHTML = pid_cutoff;
    document.getElementById("pid").value = pid_cutoff; 
}

function updatePlenLabel(plen_cutoff){
    /**
     * Updates the text of the plen-label in network.html
     */
    document.getElementById("plen-label").innerHTML = plen_cutoff;
    document.getElementById("plen").value = plen_cutoff
}

function selectElements(pid_cutoff, plen_cutoff, pname_phrase){
    /** 
     * Returns an array of edges and nodes matching cutoffs
     * Input is the pid and plen cutoffs
     * Edges meet the protein percent identity (pid) cutoff 
     * Nodes meet protein length (plen) cutoff 
     **/
    var graph_elems = []; //elements that pass criteria
    var exclude_elems = []; //elements the fail criteria
    
    var node_set = new Set();
    for(i in nodes)
    {
        n = nodes[i];
        //check protein length and whether pname_phrase is a substring of the protein name
        if (n['data']['length'] > plen_cutoff){
            if (pname_phrase == "" || pname_phrase == undefined || n['data']['name'].indexOf(pname_phrase) >= 0){
                graph_elems.push(n);
                node_set.add(n['data']['id'])
            }
        }
        else{
            exclude_elems.push(n);
        }
    }
    for (i in edges){
        e = edges[i];
        //check if the edge percent id (i.e. how similar the two proteins are) is greater than cutoff
        if (e['data']['percent_id'] > pid_cutoff){
            //check if the two nodes are present in the graph
            var edge_parents = e['data']['id'].split(',');
            if (node_set.has(edge_parents[0]) && node_set.has(edge_parents[1])){
                graph_elems.push(e);
            }
        }
        else{
            exclude_elems.push(e);
        }
    }
    //return object to parse
    return {graph_elems: graph_elems, exclude_elems:exclude_elems};
};

function buildGraph(pid_cutoff, plen_cutoff, pname_phrase){
    /**
     * Builds the cytoscape graph. 
     * Used on initialization with the global pid, plen, and pname phrases.
     * Takes these three variables to get matching nodes and edges via selectElements()
     * Then deletes the past cy graph and creates a new one
     * Adds in nodes and edges that didn't meet critera after creation so they can be seen
     * Binds the node click and edge click functions to cy
     */
    
    //set variables from global if not given
    pid_cutoff = pid_cutoff ? pid_cutoff : pid;;
    plen_cutoff = plen_cutoff ? plen_cutoff : plen;;
    pname_phrase = pname_phrase ? pname_phrase : pname;;

    pid_cutoff = parseInt(pid_cutoff);
    plen_cutoff = parseInt(plen_cutoff);
    
    //call SelectElements to parse the pairwise_parser.py output
    all_elems =  selectElements(pid_cutoff, plen_cutoff);
    //elements to include in the graph
    graph_elems = all_elems['graph_elems'];
    //elements to exclude in the graph, but to add in after creation
    exclude_elems = all_elems['exclude_elems'];
    
    //destroy previous graph
    if (typeof cy !== 'undefined') { cy.destroy(); }      
    
    //Create new cy graph with the selected elements
     new_cy = window.cy = cytoscape({
        container: document.getElementById('cy'),
        elements: graph_elems,
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
    
    //create the layout
    layout = new_cy.layout(params);
    layout.run();
    
    //run the MCL algorithm to color nodes
    mcl();

    //Add in the rest of the edges, update labels & cutoff to exclude them
    new_cy.ready(function(event){
        new_cy.add(exclude_elems);
        updatePidLabel(pid_cutoff);
        updatePlenLabel(plen_cutoff);
        updateCutoff();
    });

    //reassign to permanent variable
    cy = new_cy;

    var past_node;
    function displayNodeInfo(e){
        // var len = colors.length, text = "[";
        // for (var i = 0; i < len; i++) {            
        //     text += '"'+ colors[i] + '",'
        // }
        // text += ']'
        // document.getElementById("info").innerHTML = text;
        
        var ele = e.target;
        
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

    //on node click funciton
    var node_neighbors = null;
    cy.$('node').on('click', function(e){
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
}
//build graph initially
buildGraph();