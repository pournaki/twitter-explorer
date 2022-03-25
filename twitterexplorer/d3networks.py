## =============================================================================
## twitter explorer 
## html file builders
## =============================================================================

folder = './twitterexplorer/html/'

with open(f'{folder}head.html', 'r') as f:
    head = f.read()
with open(f'{folder}style.css', 'r') as f:
    style = f.read()

with open(f'{folder}rtn_body.html', 'r') as f:
    rtn_body = f.read()
with open(f'{folder}rtn_graph.js', 'r') as f:
    rtn_graph = f.read()
with open(f'{folder}rtn_graph_private.js', 'r') as f:
    rtn_graph_private = f.read()

with open(f'{folder}htn_body.html', 'r') as f:
    htn_body = f.read()
with open(f'{folder}htn_graph.js', 'r') as f:
    htn_graph = f.read()

with open(f'{folder}cg_rtn_body.html', 'r') as f:
    cg_rtn_body = f.read()
with open(f'{folder}cg_rtn_graph.js', 'r') as f:
    cg_rtn_graph = f.read()

with open(f'{folder}cg_htn_body.html', 'r') as f:
    cg_htn_body = f.read()
with open(f'{folder}cg_htn_graph.js', 'r') as f:
    cg_htn_graph = f.read()

def graphdata(data):
    string = \
    f"""
    <script type="text/javascript">
        var data = {data}
    </script>
    """
    return string 

def rtn_html(data):
    string = head + "\n" + \
             style + "\n" + \
             rtn_body + "\n" + \
             graphdata(data) + "\n" + \
             rtn_graph
    return string

def rtn_html_p(data):
    string = head + "\n" + \
             style + "\n" + \
             rtn_body + "\n" + \
             graphdata(data) + "\n" + \
             rtn_graph_private
    return string


def htn_html(data):
    string = head + "\n" + \
             style + "\n" + \
             htn_body + "\n" + \
             graphdata(data) + "\n" + \
             htn_graph
    return string

def cg_rtn_html(data):
    string = head + "\n" + \
             style + "\n" + \
             cg_rtn_body + "\n" + \
             graphdata(data) + "\n" + \
             cg_rtn_graph
    return string

def cg_htn_html(data):
    string = head + "\n" + \
             style + "\n" + \
             cg_htn_body + "\n" + \
             graphdata(data) + "\n" + \
             cg_htn_graph
    return string
