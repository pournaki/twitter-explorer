<script>

// initialize variables
var colorselector = document.getElementById("nodecolor");
var nodescaling = 0.05;
var nodecolor = colorselector.options[colorselector.selectedIndex].value;
var darkmode = false

// hide links by default if there are more than 10.000
if (data.links.length > 10000) {var init_linkvis = false}
else {var init_linkvis = true}

// initialize graph
const elem = document.getElementById('graph');
const Graph = ForceGraph()(elem)
.graphData({nodes: data.nodes, links: data.links})
.nodeId('id')
.nodeLabel(node => node.screen_name)
.nodeColor(node => "black")
.nodeVal(node => node.in_degree * nodescaling)
.linkDirectionalParticleColor(() => 'red')
.linkHoverPrecision(10)
.linkVisibility(init_linkvis)
.onNodeRightClick(node => { Graph.centerAt(node.x, node.y, 1000);Graph.zoom(8, 2000);})
Graph.onLinkClick(Graph.emitParticle); // emit particles on link click

// get list of all users for autocomplete
var users = []
for(var i in data.nodes)
{users.push(data.nodes[i].screen_name)};

// draw tweets
function drawortweets (){
    if (darkmode === false) {var themecol = 'light'}
    else {var themecol = 'dark'} 
    var name = document.getElementById("searchuser").value
    document.getElementById("useroriginaltweets").innerHTML = "";
    const getNode = id => {
    return data.nodes.find(node => node.screen_name === name);
    };
    var node = getNode(name)
    highlight(node)
    if (node.otweets != "None"){
    for (tweet of node.otweets) {        
        twttr.widgets.createTweet(
          tweet,
          document.getElementById('useroriginaltweets'),
          {
            theme: themecol,
            dnt: true,
            width: 280
          }
        );  }}
    else {document.getElementById('useroriginaltweets').innerHTML = "None"}
    
$("#content04").slideUp(300)
$("#content05").slideUp(300)
$("#content04A").slideDown(300);  
}

function drawretweets (){
    if (darkmode === false) {var themecol = 'light'}
    else {var themecol = 'dark'} 
    var name = document.getElementById("searchuser").value
    document.getElementById("userretweets").innerHTML = "";
    const getNode = id => {
    return data.nodes.find(node => node.screen_name === name);
    };
    var node = getNode(name)
    highlight(node)
    if (node.interactions != "None"){
    for (tweet of node.interactions) {
        if (tweet != "None") {
        twttr.widgets.createTweet(
          tweet,
          document.getElementById('userretweets'),
          {
            theme: themecol,
            dnt: true,
            width: 280
          }
        ); }       
    }}
    else {document.getElementById('userretweets').innerHTML = "None"}

$("#content04A").slideUp(300);
$("#content05").slideUp(300);
$("#content04").slideDown(300);
}


// DRAW TWITTER TIMELINE
function drawtimeline(){
if (darkmode === false) {var themecol = 'light'}
else {var themecol = 'dark'}        
var name = document.getElementById("searchuser").value
document.getElementById("twitter_timeline").innerHTML = "";
twttr.widgets.createTimeline(
{
sourceType: "profile",
screenName: name
},
document.getElementById("twitter_timeline"),
{
theme: themecol,
height: 400,
chrome: 'noscrollbar',
dnt: true                    
});
{
$("#content05").slideDown(300);
$("#content04").slideUp(300)
$("#content04A").slideUp(300)
};                  
}

// USER INFO ON CLICK
Graph.onNodeClick((node =>  {
pastenodeinfo(node);
$("#content03").slideDown(300)
$("#content01").slideUp(300)
highlight(node)
}))

function highlight(node){
var neighbors = []
neighbors.push(node)

for (link of data.links) {
  if (link.source == node) {
    neighbors.push(link.target)
    link.colorthat = 1
  }
  else if (link.target == node){
    neighbors.push(link.source)
    link.colorthat = 1
  }
  else {link.colorthat=0}
}
for (node of data.nodes){
  if(neighbors.includes(node)){
    node.colorthat = 1
  }
  else node.colorthat = 0}
colorbar = ['#d3d3d3', 'red']
Graph.nodeColor(() => 'black') 
Graph.nodeColor(node => colorbar[node.colorthat])
// linkcolor depending on dark/lightmode
if (darkmode === false) {var colorbar2 = ['rgba(0,0,0,0.05)', 'rgba(255,0,0,0.5)']}
else {var colorbar2 = ['rgba(255,255,255,0.03)', 'rgba(255,0,0,0.5)']}
Graph.linkColor(link => colorbar2[link.colorthat])
}
Graph.linkDirectionalParticles(link => {
  if (link.colorthat == 1) {
    return 1}
    else {
      return 0
    }})

Graph.onBackgroundClick(() => resetcolors())

function resetcolors(){
var bodyelement = document.querySelector('body')
var bodystyle = window.getComputedStyle(bodyelement)
var bg = bodystyle.getPropertyValue('color')
if (bg === 'rgb(0, 0, 0)') {
  var linkcol = 'rgba(0,0,0,0.2)'}
if (bg === 'rgb(255, 255, 255)') {
  var linkcol = 'rgba(255,255,255,0.2)'}

recolornodes()
Graph.linkColor(() => linkcol)}


var input = document.getElementById("searchuser");
new Awesomplete(input, {
list: users
});

// ZOOM ON USER
function zoomonuser(){
var name = document.getElementById("searchuser").value;
const getNode = id => {
return data.nodes.find(node => node.screen_name === name);
}
var nodeathand = getNode(name)
Graph.centerAt(nodeathand.x, nodeathand.y, 1000);Graph.zoom(8, 2000);
console.log(nodeathand);}

// FLASH COLOR
function flashcolor(){
var bodyelement = document.querySelector('body')
var bodystyle = window.getComputedStyle(bodyelement)
var bg = bodystyle.getPropertyValue('color')
if (bg === 'rgb(0, 0, 0)') {var nodecol = 'black'}
if (bg === 'rgb(255, 255, 255)') {var nodecol = 'white'}
var name = document.getElementById("searchuser").value;
const getNode = id => {
return data.nodes.find(node => node.screen_name === name);
};
var nodeathand = getNode(name)
console.log(nodeathand)
originalcolor = nodeathand.color
Graph.nodeColor(node => {
if (node.screen_name === name) {
return "red";
}
else {return nodecol}
});
setTimeout(function(){            
Graph.nodeColor(node => {
if (node.screen_name === name) {
return nodecol;
}
else {return nodecol}
});
}, 250);}

function resetzoom(){
Graph.centerAt(0, 0,1000);Graph.zoom(0.4, 1000)
}

// LIGHT / DARK MODE
function toggle_darkmode(){
    
    if (darkmode == false) 
    {
        document.documentElement.setAttribute('data-theme', 'darktheme');
        Graph.linkColor(() => 'rgba(255,255,255,0.2)');
        var colorselector = document.getElementById("nodecolor");
        var selectedoption = colorselector.options[colorselector.selectedIndex].value               
        if (selectedoption === "none") {Graph.nodeColor(() => 'white')}
        darkmode = true 
    }
    else 
    {
        document.documentElement.setAttribute('data-theme', 'lighttheme');
        Graph.linkColor(() => 'rgba(0,0,0,0.2)');
        var colorselector = document.getElementById("nodecolor");
        var selectedoption = colorselector.options[colorselector.selectedIndex].value                               
        if (selectedoption === "none") {Graph.nodeColor(() => 'black')}
        darkmode = false 
    }
}

// RECOLOR NODES
var colorscale = ['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4', '#46f0f0', '#f032e6', '#bcf60c', '#fabebe', '#008080', '#e6beff', '#9a6324', '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1', '#000075', '#808080', '#ffffff', '#000000']
document.getElementById("nodecolor").addEventListener("change", recolornodes);

function recolornodes(){
var colorselector = document.getElementById("nodecolor");
var selectedoption = colorselector.options[colorselector.selectedIndex].value
if (selectedoption != "none"){
Graph.nodeColor(node => colorscale[node[selectedoption]])}            
else { 
var bodyelement = document.querySelector('body')
var bodystyle = window.getComputedStyle(bodyelement)
var bg = bodystyle.getPropertyValue('color')
if (bg === 'rgb(0, 0, 0)') {var nodecol = 'black'}
if (bg === 'rgb(255, 255, 255)') {var nodecol = 'white'}
Graph.nodeColor(node => nodecol)} }

// NODE SIZE
document.getElementById("slido").addEventListener("change", rescalenodes);
function rescalenodes(){
  var nodescaleslider = document.getElementById("slido");
  var newscale = nodescaleslider.value  
  var sizeselector = document.getElementById("nodesize");
  var selectedoption = sizeselector.options[sizeselector.selectedIndex].value
  if      (selectedoption === "followers"){Graph.nodeVal(node => node[selectedoption] * 0.000005 * newscale)}            
  else if (selectedoption === "friends"){Graph.nodeVal(node => node[selectedoption] * 0.001 * newscale)}
  else if (selectedoption === "out_degree"){Graph.nodeVal(node => node[selectedoption] * 0.1 * newscale)}
  else if (selectedoption === "in_degree"){Graph.nodeVal(node => node[selectedoption] * 0.1 * newscale)}              
}

document.getElementById("nodesize").addEventListener("change", changenodesize);
function changenodesize(){
var sizeselector = document.getElementById("nodesize");
var selectedoption = sizeselector.options[sizeselector.selectedIndex].value
if      (selectedoption === "followers"){Graph.nodeVal(node => node[selectedoption] * 0.00005)}            
else if (selectedoption === "friends"){Graph.nodeVal(node => node[selectedoption] * 0.001)}
else if (selectedoption === "out_degree"){Graph.nodeVal(node => node[selectedoption] * 1.0)}
else if (selectedoption === "in_degree"){Graph.nodeVal(node => node[selectedoption] * 1.0)}              
else { Graph.nodeVal(node => 1.0)} 
}

$(function() {
var colval="none"; 
$("#nodecolor").val(colval);
});
$(function() {
var sizeval="in_degree"; 
$("#nodesize").val(sizeval);
});


// INCLUDE NETWORK INFORMATION FROM GRAPH DATA
var netinfo = `<ul> 
<li> Keyword: ${data.graph.keyword}</li>
<li> Collected on: ${data.graph.collected_on}</li>
<li> First retweet: ${data.graph.first_tweet}</li>
<li> Last retweet: ${data.graph.last_tweet}</li>
</ul>`
var netmeasures = `
<ul>
  <li>Nodes: ${data.graph.N_nodes}</li>
  <li>Links: ${data.graph.N_links}</li>
</ul>`
document.getElementById('panel00').innerHTML = data.graph.type
document.getElementById('content00').innerHTML = netinfo
document.getElementById('content02').innerHTML = netmeasures
document.getElementById('version_number').innerHTML = data.version_number

// NODE INFO
function pastenodeinfo(node){
userinfostring = `<ul> 
<li> Followers: ${node.followers}
<li> Followed accounts: ${node.friends}
<li> Times the user ${interaction_type_past.split(' ')[0]}: ${node.out_degree}
<li> Times the user got ${interaction_type_past}: ${node.in_degree}
</ul>`
document.getElementById('userinfostring').innerHTML = userinfostring
document.getElementById("searchuser").value = node.screen_name
}


var interaction_type = data.graph.type.split(' ')[0].toLowerCase()

if (interaction_type == "retweet"){
    document.getElementById('indegreeoption').innerHTML = "In-Degree (Number of times the account got retweeted)"
    document.getElementById('outdegreeoption').innerHTML = "Out-Degree (Number of times the account retweeted another)"    
    document.getElementById('panel04').innerHTML = "RETWEETS IN DATASET"
    document.getElementById('fetch_interaction').innerHTML = "Fetch retweets"
    var interaction_type_past = "retweeted"
}

if (interaction_type == "quote"){
    document.getElementById('indegreeoption').innerHTML = "In-Degree (Number of times the account got quoted)"
    document.getElementById('outdegreeoption').innerHTML = "Out-Degree (Number of times the account quoted another)"    
    document.getElementById('panel04').innerHTML = "QUOTES IN DATASET"
    document.getElementById('fetch_interaction').innerHTML = "Fetch quotes"
    var interaction_type_past = "quoted"
}
if (interaction_type == "reply"){
    document.getElementById('indegreeoption').innerHTML = "In-Degree (Number of times the account got replied to)"
    document.getElementById('outdegreeoption').innerHTML = "Out-Degree (Number of times the account replied to another)"    
    document.getElementById('panel04').innerHTML = "REPLIES IN DATASET"
    document.getElementById('fetch_interaction').innerHTML = "Fetch replies"
    var interaction_type_past = "replied to"
}
if (interaction_type == "mention"){
    document.getElementById('indegreeoption').innerHTML = "In-Degree (Number of times the account got mentioned)"
    document.getElementById('outdegreeoption').innerHTML = "Out-Degree (Number of times the account mentioned another)"    
    document.getElementById('panel04').innerHTML = "MENTIONS IN DATASET"
    document.getElementById('fetch_interaction').innerHTML = "Fetch mentions"
    var interaction_type_past = "mentioned"
    document.getElementById('fetch_originaltweet').style="display:none"
    document.getElementById('originaltweetsborders').style="display:none"    
}

$("#content00").slideToggle(300)

function toggle_linkvisibility(){
    if (Graph.linkVisibility() == true){
        Graph.linkVisibility(false)
    }
    else {Graph.linkVisibility(true)}
}

function make_screenshot(){
// var canvas = document.getElementsByClassName('force-graph-container')[0]['children'][0];
var canvas = document.getElementById('graph')['children'][0]['children'][0]
console.log(canvas)
var link = document.getElementById('camera');
link.setAttribute('download', 'screenshot.png');
link.setAttribute('href', canvas.toDataURL("image/png").replace("image/png", "image/octet-stream"));
link.click()
}

function export_nodes_as_csv(){
    var csv_string = ""
    var options = Object.keys(data.nodes[0])
    var to_disregard = ['otweets','interactions','__indexColor','x','y','vx','vy','index']
    var filtered_options = options.filter(function(e) { return !to_disregard.includes(e)})
    for (option of filtered_options)
        {csv_string += option;csv_string += ","}
    csv_string = csv_string.slice(0, -1)
    csv_string += "\n"
    for (var i = 0; i < data.nodes.length; ++i)
    // for (var i = 0; i < 2; ++i)
        {
            node = data.nodes[i]
            for (option of filtered_options){
                csv_string += node[option]
                csv_string += ","
            }
            csv_string = csv_string.slice(0, -1)
            csv_string += "\n"
        }
    csv_string = csv_string.slice(0, -1)
    var blob = new Blob([csv_string],
      { type: "text/plain;charset=utf-8" });
    saveAs(blob, "nodes_metadata.csv");
}

function d3graph_to_gml(){
  var gml_string = "graph\n[\n"
  var options = Object.keys(data.nodes[0])
  var to_disregard = ['otweets','interactions']
  var filtered_options = options.filter(function(e) { return !to_disregard.includes(e)})
  for (var i = 0; i < data.nodes.length; ++i){
    node = data.nodes[i]
    gml_string += "node\n"
    gml_string += "[\n"
    for (option of filtered_options){
      if (node[option].constructor !== Array || typeof node[option] !== 'object') {
      if (typeof node[option] === 'string' || node[option] instanceof String){
        gml_string += option + " " + '"' + node[option] + '"' + "\n"
      }
      else {
      gml_string += option + " " + node[option] + "\n"
    }}}
    gml_string += "]\n"
  }
  for (var i = 0; i < data.links.length; ++i){
    link = data.links[i], source = link.source, target = link.target;
    gml_string += "edge\n"
    gml_string += "[\n" 
    gml_string += "source " + source.id + "\n"
    gml_string += "target " + target.id + "\n"
    gml_string += "]\n"
  }
  gml_string += "]"
  var blob = new Blob([gml_string],
      { type: "text/plain;charset=utf-8" });
  saveAs(blob, "network.gml");
}

</script>

</body>