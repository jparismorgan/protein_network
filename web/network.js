//End of protein elements.

var initial_pid_cutoff = 90;

var params_style = [{
        selector: 'node',
            style: {
           // 'content': 'data(name)',
            'width': 50,//'mapData(num_cluster_members, 0, 150, 50,  300)',
            'height': 50,//'mapData(num_cluster_members, 0, 150, 50, 300)', 
            }
        },
        {
        selector: 'edge',
            css: {
                'width': 10,
                'line-color': "#A9A9A9",
            }
        },
    ];

 var params = {
        name: 'cola',
        pixelRatio: 1, //performance optimization
        hideEdgesOnViewport: true, //performance
        textureOnViewport: true, //performance optimization
        nodeSpacing: function( node ){ return 1;  },
        randomize: false,
        edgeLength: function( edge ){
            var len = parseInt(edge.data('weight')); 
            return 10 / len ; 
        },
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
function mcl(){
    // Run Markov cluster on graph
    var clusters = cy.elements().markovCluster( mcl_options );
    
    // Assign random colors to each cluster!
    for (var c = 0; c < clusters.length; c++) {
        clusters[c].style( 'background-color', '#'+Math.random().toString(16).slice(-3));
        //clusters[c].style( 'background-color', '#' + Math.floor(Math.random()*16777215).toString(16) );
    }
};

var removed_elems_pid;
function updatePercentIdCutoff(percent_id_cuttoff){
    
    //Previous method: remove edges from graph
    document.getElementById("currentValue").innerHTML = percent_id_cuttoff;
      if (removed_elems_pid){
          removed_elems_pid.restore();};
      removed_elems_pid = cy.elements("edge[percent_id < " + percent_id_cuttoff+ "]");
      cy.remove(removed_elems_pid);

    //New method: create new layout
    // new_elems = cy.elements("edge[percent_id > " + percent_id_cuttoff+ "], node");
    // layout.stop();      
    // new_layout = new_elems.layout(params);
    // new_layout.run();
    //new_layout.style(params_style);
    
    //mcl();
}

function updatePercentIdLabel(percent_id_cuttoff){
    document.getElementById("currentValue").innerHTML = percent_id_cuttoff;
}

var cy;
var layout;
function updateElements(element_cuttoff){
    new_elems =  window['elems_'+element_cuttoff];
    
    if (typeof cy !== 'undefined') { cy.destroy(); }      
    
     new_cy = window.cy = cytoscape({
        container: document.getElementById('cy'),
        elements: new_elems,
        zoom: 1,
        minZoom: .1,
        maxZoom: 2,
        style: [{
        selector: 'node',
            style: {
           // 'content': 'data(name)',
            'width': 50, //'mapData(num_cluster_members, 0, 150, 80,  300)',
            'height': 50 //'mapData(num_cluster_members, 0, 150, 80, 300)', 
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

    cy = new_cy;
    mcl();
}

updateElements(90);

var node_neighbors = null;
cy.$('node').on('click', function(e){
    var ele = e.target;
    //Update info box
    document.getElementById("info").innerHTML = "Node: " + ele.data('id') + "<br> Num Cluster Members: " + ele.data('num_cluster_members');
    console.log(ele);
    
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
  document.getElementById("info").innerHTML = info_text;
});



mcl();
// updatePercentIdCutoff(initial_pid_cutoff);
// updatePercentIdLabel(initial_pid_cutoff);
