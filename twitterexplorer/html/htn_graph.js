<script>
var colorselector = document.getElementById("nodecolor");
var nodescaling = 3;
var darkmode = false

// get node color options
ms = document.getElementById('nodecolor')
if ('louvain_com' in data.nodes[0]){ms.innerHTML+=`<option value = "louvain_com">Louvain community</option>\n`}
if ('leiden_com' in data.nodes[0]){ms.innerHTML+=`<option value = "leiden_com">Leiden community</option>\n`}

var nodecolor = colorselector.options[colorselector.selectedIndex].value;
const elem = document.getElementById('graph');
const Graph = ForceGraph()(elem)
.graphData({nodes: data.nodes, links: data.links})
.nodeColor(node => "black")
.nodeLabel("")
.nodeCanvasObject((node, ctx, globalScale) => {
  const label = node.name;
  const fontSize = Math.log(1+node.degree) * nodescaling
  ctx.font = `${fontSize}px Inter`;
  const textWidth = ctx.measureText(label).width;
  const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.1); // some padding

  ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
  // ctx.fillRect(node.x - bckgDimensions[0] / 2, node.y - bckgDimensions[1] / 2, ...bckgDimensions);

  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillStyle = "black";
  ctx.fillText("#"+label, node.x, node.y);
}) 
.nodeId('id')
.linkHoverPrecision(10)
.linkColor(link => 'rgba(0,0,0,0.1)')
.onNodeClick(node => {highlight(node)})
.onNodeRightClick(node => { Graph.centerAt(node.x, node.y, 1000);Graph.zoom(8, 2000);})

// Get the list of all users for autocomplete
var users = []
for(var i in data.nodes)
  users.push(data.nodes[i].name);

var name = document.getElementById("searchuser").value;

        function highlight(node){
    $("#content03").slideDown(300);
    pastenodeinfo(node);
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
    var nodescaleslider = document.getElementById("slido");
    var newscale = nodescaleslider.value  
  
    Graph.nodeCanvasObject((node, ctx, globalScale) => {
          const label = node.name;
          const fontSize = Math.log(1+node.degree) * newscale
          ctx.font = `${fontSize}px Inter`;
          const textWidth = ctx.measureText(label).width;
          const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.1); // some padding

          ctx.fillStyle = 'rgba(255, 255, 255, 1.0)';
          // ctx.fillRect(node.x - bckgDimensions[0] / 2, node.y - bckgDimensions[1] / 2, ...bckgDimensions);

          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillStyle = colorbar[node.colorthat];
          ctx.fillText("#"+label, node.x, node.y);
        })
    // linkcolor depending on dark/lightmode
    var bodyelement = document.querySelector('body')
    var bodystyle = window.getComputedStyle(bodyelement)
    var bg = bodystyle.getPropertyValue('color')
    if (bg === 'rgb(0, 0, 0)') {var colorbar2 = ['rgba(0,0,0,0.05)', 'rgba(255,0,0,0.5)']}
    if (bg === 'rgb(255, 255, 255)') {var colorbar2 = ['rgba(255,255,255,0.03)', 'rgba(255,0,0,0.5)']}
    Graph.linkColor(link => colorbar2[link.colorthat])
    }
    Graph.onBackgroundClick(() => resetcolors())

    function resetcolors(){
    var colorselector = document.getElementById("nodecolor");
    var selectedoption = colorselector.options[colorselector.selectedIndex].value

    var nodescaleslider = document.getElementById("slido");
    var newscale = nodescaleslider.value  
    
        Graph.nodeCanvasObject((node, ctx, globalScale) => {
          const label = node.name;
          const fontSize = Math.log(1+node.degree) * newscale
          ctx.font = `${fontSize}px Inter`;
          const textWidth = ctx.measureText(label).width;
          const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.1); // some padding

          ctx.fillStyle = 'rgba(255, 255, 255, 1.0)';
          // ctx.fillRect(node.x - bckgDimensions[0] / 2, node.y - bckgDimensions[1] / 2, ...bckgDimensions);

          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
        if (selectedoption == "louvain_com" ) {ctx.fillStyle = colorscale[node["louvain_com"]];}
        else if (selectedoption == "leiden_com" ) {ctx.fillStyle = colorscale[node["leiden_com"]];}                
        else { if (darkmode == true) {ctx.fillStyle = "white";} else {ctx.fillStyle = "black";}}
          ctx.fillText("#"+label, node.x, node.y);
        })
        if (darkmode == false){Graph.linkColor(link => 'rgba(0,0,0,0.1)')}
        else {Graph.linkColor(link => 'rgba(255,255,255,0.2)')}
        
        }
var input = document.getElementById("searchuser");
new Awesomplete(input, {
list: users
  });
var name = document.getElementById("searchuser").value;

// var searcheduser = document.getElementById("searchuser").value;

function zoomonuser(){
  var name = document.getElementById("searchuser").value;
  const getNode = id => {
      return data.nodes.find(node => node.name === name);
  }
  var nodeathand = getNode(name)
  Graph.centerAt(nodeathand.x, nodeathand.y, 1000);Graph.zoom(8, 2000);
  }

function resetzoom(){
  Graph.centerAt(0, 0,1000);Graph.zoom(0.8, 1000)
}

// LIGHT / DARK MODE
function toggle_darkmode() {
var colorselector = document.getElementById("nodecolor");
var bytype = colorselector.options[colorselector.selectedIndex].value
var nodescaleslider = document.getElementById("slido");
var newscale = nodescaleslider.value  

if (darkmode == false) {
darkmode = true
document.documentElement.setAttribute('data-theme', 'darktheme');
Graph.linkColor(() => 'rgba(255,255,255,0.2)');
Graph.nodeCanvasObject((node, ctx, globalScale) => {
      const label = node.name;
      const fontSize = Math.log(1+node.degree) * newscale
      ctx.font = `${fontSize}px Inter`;
      const textWidth = ctx.measureText(label).width;
      const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.1); // some padding

      // ctx.fillRect(node.x - bckgDimensions[0] / 2, node.y - bckgDimensions[1] / 2, ...bckgDimensions);

      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      if (bytype == "louvain_com"){ctx.fillStyle = colorscale[node["louvain_com"]]}
      else if (bytype == "leiden_com"){ctx.fillStyle = colorscale[node["leiden_com"]]}        
      else {ctx.fillStyle = "white"}
      ;
      ctx.fillText("#"+label, node.x, node.y);
    })
}

else {
darkmode = false   
document.documentElement.setAttribute('data-theme', 'lighttheme');
Graph.linkColor(() => 'rgba(0,0,0,0.2)');
Graph.nodeCanvasObject((node, ctx, globalScale) => {
      const label = node.name;
      const fontSize = Math.log(1+node.degree) * newscale
      ctx.font = `${fontSize}px Inter`;
      const textWidth = ctx.measureText(label).width;
      const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.1); // some padding

      // ctx.fillStyle = 'rgba(255, 255, 255, 1.0)';
      // ctx.fillRect(node.x - bckgDimensions[0] / 2, node.y - bckgDimensions[1] / 2, ...bckgDimensions);

      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      if (bytype == "louvain_com"){ctx.fillStyle = colorscale[node["louvain_com"]]}
      else if (bytype == "leiden_com"){ctx.fillStyle = colorscale[node["leiden_com"]]}        
      else {ctx.fillStyle = "black"}
      ;
      ctx.fillText("#"+label, node.x, node.y);
    })
}    
}

var colorscale = ['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4', '#46f0f0', '#f032e6', '#bcf60c', '#fabebe', '#008080', '#e6beff', '#9a6324', '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1', '#000075', '#808080', '#ffffff', '#000000']

function changecolor(bytype) {

var nodescaleslider = document.getElementById("slido");
var newscale = nodescaleslider.value  

Graph.nodeCanvasObject((node, ctx, globalScale) => {
      const label = node.name;
      const fontSize = Math.log(1+node.degree) * newscale
      ctx.font = `${fontSize}px Inter`;
      const textWidth = ctx.measureText(label).width;
      const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.1); // some padding

      ctx.fillStyle = 'rgba(255, 255, 255, 1.0)';
      // ctx.fillRect(node.x - bckgDimensions[0] / 2, node.y - bckgDimensions[1] / 2, ...bckgDimensions);

      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      if (bytype == "louvain_com"){ctx.fillStyle = colorscale[node["louvain_com"]]}
      else if (bytype == "leiden_com"){ctx.fillStyle = colorscale[node["leiden_com"]]}        
      else {ctx.fillStyle = "black"}
      ;
      ctx.fillText("#"+label, node.x, node.y);
    })}

document.getElementById("nodecolor").addEventListener("change", recolornodes);
function recolornodes(){

  var colorselector = document.getElementById("nodecolor");
  var selectedoption = colorselector.options[colorselector.selectedIndex].value
  console.log(selectedoption)
  if (selectedoption != "none"){
  changecolor(selectedoption)}            
  else { 
  var bodyelement = document.querySelector('body')
  var bodystyle = window.getComputedStyle(bodyelement)
  var bg = bodystyle.getPropertyValue('color')
  if (bg === 'rgb(0, 0, 0)') {var nodecol = 'black'}
  if (bg === 'rgb(255, 255, 255)') {var nodecol = 'white'}
  changecolor("none")} }

function openhashtag(){ 
  var hashtagname = document.getElementById("searchuser").value;
  window.open(`https://twitter.com/search?q=%23${hashtagname}`, '_blank');
  }

// NODE SIZE
document.getElementById("slido").addEventListener("change", rescalenodes);
function rescalenodes(){
  var colorselector = document.getElementById("nodecolor");
  var selectedoption = colorselector.options[colorselector.selectedIndex].value
  var nodescaleslider = document.getElementById("slido");
  var newscale = nodescaleslider.value  
  Graph.nodeCanvasObject((node, ctx, globalScale) => {
    const label = node.name;
    const fontSize = Math.log(1+node.degree) * newscale
    ctx.font = `${fontSize}px Inter`;
    const textWidth = ctx.measureText(label).width;
    const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.1); // some padding

    ctx.fillStyle = 'rgba(255, 255, 255, 1.0)';
    // ctx.fillRect(node.x - bckgDimensions[0] / 2, node.y - bckgDimensions[1] / 2, ...bckgDimensions);

    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';

    if (selectedoption == "louvain_com" ) {ctx.fillStyle = colorscale[node["louvain_com"]];}
    else if (selectedoption == "leiden_com" ) {ctx.fillStyle = colorscale[node["leiden_com"]];}    
    else {ctx.fillStyle = "black";}
    
    ctx.fillText("#"+label, node.x, node.y);
  })  

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
$(function() {
var sizeval="degree"; 
$("#nodesize").val(sizeval);
});

function toggle_linkvisibility(){
    if (Graph.linkVisibility() == true){
        Graph.linkVisibility(false)
    }
    else {Graph.linkVisibility(true)}
}

// NODE INFO ON HOVER
function pastenodeinfo(node){
userinfostring = `<ul> 
<li> Degree: ${node.degree}
</ul>`
document.getElementById('userinfostring').innerHTML = userinfostring
document.getElementById("searchuser").value = node.name}

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
document.getElementById('version_number').innerHTML = data.version_number

// NODE REPULSION
document.getElementById("repulsion_slider").addEventListener("change", rescale_repulsion);
function rescale_repulsion(){
  var repulsion_slider = document.getElementById("repulsion_slider");
  var newscale_repulsion = repulsion_slider.value 
  Graph.d3ReheatSimulation() 
  Graph.d3Force('charge').strength(-newscale_repulsion)
}

</script>
</body>