<script>
var colorselector = document.getElementById("nodecolor");
var nodescaling = 0.1;
      var nodecolor = colorselector.options[colorselector.selectedIndex].value;
      const elem = document.getElementById('graph');
      const Graph = ForceGraph()(elem)
      .graphData({nodes: data.nodes, links: data.links})
      .nodeColor(node => "black")
      .nodeId('name')
      .nodeLabel(node => '#'+node.name)
      .nodeVal(node => node.degree * nodescaling)
      .linkDirectionalParticleColor(() => 'red')
      .linkHoverPrecision(10)
      .linkCurvature(0.01)
      .onNodeClick(node => $("#content03").slideDown(300))

      .onNodeRightClick(node => { Graph.centerAt(node.x, node.y, 1000);Graph.zoom(8, 2000);})

      // Get the list of all users for autocomplete
      var users = []
      for(var i in data.nodes)
          users.push(data.nodes[i].name);

      var name = document.getElementById("searchuser").value;

var input = document.getElementById("searchuser");
new Awesomplete(input, {
list: users
  });
var name = document.getElementById("searchuser").value;
console.log(name);
// var searcheduser = document.getElementById("searchuser").value;

function zoomonuser(){
  var name = document.getElementById("searchuser").value;
  const getNode = id => {
      return data.nodes.find(node => node.name === name);
  }
  var nodeathand = getNode(name)
  Graph.centerAt(nodeathand.x, nodeathand.y, 1000);Graph.zoom(8, 2000);
  console.log(nodeathand);}

function flashcolor(){
  var bodyelement = document.querySelector('body')
  var bodystyle = window.getComputedStyle(bodyelement)
  var bg = bodystyle.getPropertyValue('color')
  if (bg === 'rgb(0, 0, 0)') {var nodecol = 'black'}
  if (bg === 'rgb(255, 255, 255)') {var nodecol = 'white'}
  var name = document.getElementById("searchuser").value;
  const getNode = id => {
      return data.nodes.find(node => node.name === name);
  };
  var nodeathand = getNode(name)
  console.log(nodeathand)
  originalcolor = nodeathand.color
  Graph.nodeColor(node => {
    if (node.name === name) {
      return "red";
        }
    else {return nodecol}
          });
  setTimeout(function(){            
    Graph.nodeColor(node => {
    if (node.name === name) {
      return nodecol;
        }
    else {return nodecol}
          });
    }, 250);}

function resetzoom(){
  Graph.centerAt(0, 0,1000);Graph.zoom(0.8, 1000)
}

var checkbox = document.querySelector('input[name=mode]');      
checkbox.addEventListener('change', function() {
  if(this.checked) {
      trans()
      document.documentElement.setAttribute('data-theme', 'darktheme');
      Graph.linkColor(() => 'rgba(255,255,255,0.2)');
      var colorselector = document.getElementById("nodecolor");
      var selectedoption = colorselector.options[colorselector.selectedIndex].value               
      if (selectedoption === "none") {Graph.nodeColor(() => 'white')}
      } 
    else {
      trans()
      document.documentElement.setAttribute('data-theme', 'lighttheme');
      Graph.linkColor(() => 'rgba(0,0,0,0.2)');
      var colorselector = document.getElementById("nodecolor");
      var selectedoption = colorselector.options[colorselector.selectedIndex].value                               
      if (selectedoption === "none") {Graph.nodeColor(() => 'black')}
  }
})
let trans = () => {
  document.documentElement.classList.add('transition');
  window.setTimeout(() => {
      document.documentElement.classList.remove('transition');
  }, 1000)
}

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

function openhashtag(){ 
  var hashtagname = document.getElementById("searchuser").value;
  window.open(`https://twitter.com/search?q=%23${hashtagname}`, '_blank');
  }

// NODE SIZE
document.getElementById("slido").addEventListener("change", rescalenodes);
function rescalenodes(){
  var nodescaleslider = document.getElementById("slido");
  var newscale = nodescaleslider.value  
  var sizeselector = document.getElementById("nodesize");
  var selectedoption = sizeselector.options[sizeselector.selectedIndex].value
  if (selectedoption === "degree"){Graph.nodeVal(node => node[selectedoption] * 0.05 * newscale)}
  else { Graph.nodeVal(node => 1.0 * newscale)}            
}

document.getElementById("nodesize").addEventListener("change", changenodesize);
function changenodesize(){
var sizeselector = document.getElementById("nodesize");
var selectedoption = sizeselector.options[sizeselector.selectedIndex].value
if (selectedoption === "degree"){Graph.nodeVal(node => node[selectedoption] * 0.05)}            
else { Graph.nodeVal(node => 1.0)} 
}

$(function() {
var sizeval="degree"; 
$("#nodesize").val(sizeval);
});

// NODE INFO ON HOVER
function pastenodeinfo(node){
userinfostring = `<ul> 
<li> Degree: ${node.degree}
</ul>`
document.getElementById('userinfostring').innerHTML = userinfostring
document.getElementById("searchuser").value = node.name}
Graph.onNodeHover(node => node && pastenodeinfo(node))

var netinfo = `<ul> 
<li> Keyword: ${data.graph.keyword}</li>
<li> Collected on: ${data.graph.collected_on}</li>
<li> First tweet: ${data.graph.first_tweet}</li>
<li> Last tweet: ${data.graph.last_tweet}</li>
</ul>`
var netmeasures = `
<ul>
  <li>Nodes: ${data.graph.N_nodes}</li>
  <li>Links: ${data.graph.N_links}</li>
</ul>`
document.getElementById('panel00').innerHTML = data.graph.type
document.getElementById('content00').innerHTML = netinfo
document.getElementById('content02').innerHTML = netmeasures
</script>
</body>