//End of protein elements.
var params = {
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

var mcl_options = {
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

var cy;
var layout;
var init_pid_cutoff = 90;
var init_plen_cutoff = 90;

//to delete
var colors = []

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

function selectElements(pid_cutoff, plen_cutoff){
    /** 
     * Returns an array of edges and nodes matching cutoffs
     * Input is the pid and plen cutoffs
     * Edges meet the protein percent identity (pid) cutoff 
     * Nodes meet protein length (plen) cutoff */
    graph_elems = [];
    exclude_elems = [];
    for(i in nodes)
    {
        n = nodes[i];
        if (n['data']['length'] > plen_cutoff){
            graph_elems.push(n);
             }
        else{
            exclude_elems.push(n);
        }
    }
    for (i in edges){
        e = edges[i];
        if (e['data']['percent_id'] > pid_cutoff){
            graph_elems.push(e);
            }
        else{
            exclude_elems.push(e);
        }
    }
    return {graph_elems: graph_elems, exclude_elems:exclude_elems};
};

var removed_nodes = [];
var removed_edges;
function updateCutoff(){
    /** 
     * Updates the network graph according to cutoffs
     * Uses protein percent identity (pid), protein length (plen), and protein name substring (pname)  
     * These are stored in network.html forms and buttons.
     */
    
    //get the pid, plen, and pname
    pid = document.getElementById('pid').value;
    plen = document.getElementById('plen').value;
    pname = document.getElementById('pname').value;
    
    //restore nodes
    if (removed_nodes){
        for (i in removed_nodes){
            removed_nodes[i].restore();
        }
    }
    //restore edges
    if (removed_edges){
        removed_edges.restore();
    }

    //remove nodes by pname
    if (pname !== "" || pname !== undefined){
        rem_pname = cy.elements('node[protein_name !*="' + pname + '"]');
        removed_nodes.push(rem_pname);
        cy.remove(rem_pname);
    }

    //remove nodes by plen
    rem_plen = cy.elements("node[length < " + plen + "]");
    removed_nodes.push(rem_plen);
    cy.remove(rem_plen);

    //remove edges by pid
    rem_pid = cy.elements("edge[percent_id < " + pid+ "]");
    removed_edges = rem_pid;
    cy.remove(rem_pid);

    //update html span's
    document.getElementById("pname-label").innerHTML = "Search term: " + pname;
    document.getElementById("plength-label").innerHTML = plen;
    document.getElementById("pid-label").innerHTML = pid;

}

function updatePidLabel(pid_cutoff){
    document.getElementById("pid-label").innerHTML = pid_cutoff;
}

function updatePlenLabel(plen_cutoff){
    document.getElementById("pid-label").innerHTML = plen_cutoff;
}

function buildGraph(pid_cutoff, plen_cutoff){

    all_elems =  selectElements(pid_cutoff, plen_cutoff);
    graph_elems = all_elems['graph_elems'];
    exclude_elems = all_elems['exclude_elems'];
    console.log(graph_elems);
    
    if (typeof cy !== 'undefined') { cy.destroy(); }      
    
    //Create new cy graph with the selected elements
     new_cy = window.cy = cytoscape({
        container: document.getElementById('cy'),
        elements: graph_elems,
        zoom: .1,
        minZoom: .05,
        maxZoom: .2,
        style: [{
        selector: 'node',
            style: {
           // 'content': 'data(name)',
            'width': 'mapData(num_cluster_members, 0, 150, 40,  90)',
            'height': 'mapData(num_cluster_members, 0, 150, 40, 90)', 
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
    
    layout = new_cy.layout(params);
    layout.run();
    mcl();

    cy = new_cy;

    //Add in al the edges, set timeout so they are not part of the initial layout
    cy.on('click', function(event){
        setTimeout(10000);
        new_cy.add(exclude_elems);
        updateCutoff();
    });

    var node_neighbors = null;
    cy.$('node').on('click', function(e){
        
        // var len = colors.length, text = "[";
        // for (var i = 0; i < len; i++) {            
        //     text += '"'+ colors[i] + '",'
        // }
        // text += ']'
        // document.getElementById("info").innerHTML = text;

        var ele = e.target;
        console.log(ele.data());
        
        //Update info box
        info_text = ""
        info_text += 'protein_name: ' + ele.data('protein_name') + '<br>'
        info_text += 'source_organism: ' + ele.data('source_organism') + '<br>'
        info_text += 'length: ' + ele.data('length') +  '<br>'
        info_text += 'NCBI_taxonomy: ' + ele.data('NCBI_taxonomy') + '<br>'
        info_text += 'UniProtKB_accession: <a href="http://www.uniprot.org/uniprot/' + ele.data('UniProtKB_accession') +'">' +ele.data('UniProtKB_accession')+'</a><br>'
        info_text += 'num_cluster_members: ' + ele.data('num_cluster_members') + '<br>'
        
        //Protein name: " + ele.data('id') + "<br> Num Cluster Members: " + ele.data('num_cluster_members');
        console.log(info_text);
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
    });

    cy.$('edge').on('click', function(e){
        var ele = e.target;
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

buildGraph(init_pid_cutoff, init_plen_cutoff);
