## =============================================================================
## twitter explorer visualizer 
## streamlit interface
## =============================================================================

import sys
sys.path.append("/Users/ap/git/twitter-explorer/")

import os
import pandas as pd
import numpy as np
import altair as alt
import streamlit as st
import datetime as dt

from twitterexplorer.legacy import *
from twitterexplorer.helpers import *
from twitterexplorer.streamlitutils import *
from twitterexplorer.plotting import *
from twitterexplorer.converters import twitterjsonl_to_twitwicsv
from twitterexplorer.converters import export_graph
from twitterexplorer.defaults import *
from twitterexplorer.constants import *
from twitterexplorer.__version__ import __version__
from twitterexplorer.networks import InteractionNetwork
from twitterexplorer.networks import SemanticNetwork

ui_changes()

st.title("Visualizer")

datapath = st.text_input(label="Path to downloaded Twitter data",
                         value=DEFAULT_DATA_DIR
                         )

filename = file_selector(datapath)

if filename not in [datapath+"---",datapath+"\\---"]:

    filesize = os.path.getsize(filename) >> 20

    if filename[-1] == "l":
        subtitlevalue = filename.replace(datapath,"")[11:-6]
    else:
        subtitlevalue = filename.replace(datapath,"")[11:-4]

    collectedon = filename.replace(datapath,"")[:10]
    subtitle = subtitlevalue

    project = st.text_input(label="Set a foldername for the project that will be \
        created in ./output",
                            value=f"{collectedon}_{subtitle}")

    st.write(f'`You selected {filename}.`<br>\
        `The file size is about {filesize}MB.`', unsafe_allow_html=True)

    outputdir = DEFAULT_OUTPUT_DIR
    projectdir = outputdir + project

    @st.cache
    def load_data(path):
        try:
            df = pd.read_csv(path,
                             dtype=twitwi_schema,
                             usecols=cols_to_load,
                             low_memory=False,
                             # lineterminator='\n'
                         )          
            df = df.drop_duplicates('id',keep='last')        
        except (pd.errors.ParserError,ValueError) as e:
            df = pd.read_csv(path,
                             dtype=twitwi_schema,
                             usecols=cols_to_load,
                             low_memory=False,
                             lineterminator='\n'
                         )          
            df = df.drop_duplicates('id',keep='last')                
        return df    

    if filename[-3:] == "csv":
        df = load_data(filename)
    elif filename[-5:] == "jsonl":
        ## convert to twitwi csv
        with st.spinner("Converting to twitwi csv..."):
            twitterjsonl_to_twitwicsv(filename)
        filename = filename.replace("jsonl","csv")
        df = load_data(filename)
    
    timeseries = tweetdf_to_timeseries(df,frequency="1H")
    timeseries_plot = plot_timeseries(timeseries)
    st.altair_chart(timeseries_plot, use_container_width=True)

    langbars = plot_tweetlanguages(df)
    st.altair_chart(langbars, use_container_width=True)

    st.write("---")

    # -------------------------------------------------------------------

    st.header("Interactive networks")

    st.write("Create interaction networks and semantic networks.")

    if st.checkbox("Custom timerange"):
        # guess the default daterange from the filename
        try:
            today = dt.date.fromisoformat(filename[7:17])
            lastweek = today + dt.timedelta(days=-8)
        except ValueError:
            today = dt.date.today()
            lastweek = today + dt.timedelta(days=-8)

        daterange = st.date_input(label="Timerange for creating networks:",
                                  value=[lastweek,
                                         today])
        d0 = daterange[0]
        d1 = daterange[1]
        ts0 = int(date_to_datetime(daterange[0]).timestamp())
        ts1 = int(date_to_datetime(daterange[1]).timestamp())
        ts1 += 86399 # to use the whole day
    else:
        ts0 = None
        ts1 = None

    langselector_iso = None

    if st.checkbox("Language filter"):
        with open (PACKAGE_DIR+"/languages.json", 'r', encoding='utf-8') as f:
            iso_to_language = json.load(f)
        language_to_iso = {v: k for k, v in iso_to_language.items()}        
        langcounts = pd.DataFrame(df.groupby('lang')["id"].count()).reset_index().rename(columns={'id':'count'}).sort_values(by='count', ascending=False)
        langcounts['lang_name'] = langcounts['lang'].map(iso_to_language)
        langselector = st.multiselect(label='Select languages to filter', 
                     options=langcounts['lang_name'],
                     # format_func=lambda x: f"{x['language']} / {x['count']}"
                     )        
        langselector_iso = []
        for lang in langselector:
            iso = language_to_iso[lang]
            langselector_iso.append(iso)
    else:
        langselector = None    
    if langselector_iso == []:
        langselector_iso = None

    with st.expander("INTERACTION NETWORK"):
        st.write()
        interaction_type = st.selectbox(label='Interaction type',
                                        options=['retweet','reply','quote','mention'])
        if interaction_type == 'retweet':
            st.write("Directed network in which nodes are users. A link is drawn from \
                `i` to `j` if `i` retweets `j`.")
        elif interaction_type == 'reply':
            st.write("Directed network in which nodes are users. A link is drawn from \
                `i` to `j` if `i` replies to `j`.")
        elif interaction_type == 'quote':
            st.write("Directed network in which nodes are users. A link is drawn from \
                `i` to `j` if `i` quotes `j`.")
        elif interaction_type == 'mention':
            st.write("Directed network in which nodes are users. A link is drawn from \
                `i` to `j` if `i` mentions `j`.")

        st.write('<span style="text-decoration: underline;">Options</span>', 
                 unsafe_allow_html=True)
        rtn_giantcomponent = st.checkbox("Giant component", key='rtn_giantcomponent', help="Reduce the network to its largest connected component.")
        privacy = st.checkbox(
            "Remove metadata of nodes that are not public figures \
             (less than 5000 followers)")
        rtn_export = st.checkbox("Export the graph to GML, GV and Edgelist",key="rtn_export")
        st.write('<span style="text-decoration: underline;">Aggregation method</span>', 
                 unsafe_allow_html=True)
        rtn_aggregation_soft = st.checkbox(
            "Soft aggregate (remove nodes with in-degree 0 and only one neighbor)",
            key='rtn_aggregation_soft')
        rtn_aggregation_hard = st.checkbox(
            "Hard aggregate (remove nodes with in-degree < threshold)",
            key='rtn_aggregation_hard')
        hard_aggregation_threshold = 0
        if rtn_aggregation_hard:
            thresh_rtn = st.slider("Hard aggregation threshold", 0, 20, 1, 1, key='thresh_rtn')
            hard_aggregation_threshold += thresh_rtn
        if rtn_aggregation_soft:
            aggregationmethod = 'soft'
        elif rtn_aggregation_hard:
            aggregationmethod = 'hard'
        else:
            aggregationmethod = None
        if rtn_aggregation_soft is True and rtn_aggregation_hard is True:
            st.error("Please choose only one of the aggregations")

        st.write('<span style="text-decoration: underline;">Community detection</span>', 
                 unsafe_allow_html=True)
        rtn_louvain = st.checkbox("Louvain", key='rtn_louvain', help="Requires the installation of the 'louvain' package, currently not working on M1 machines.")
        rtn_leiden = st.checkbox("Leiden", key='rtn_leiden')

        if st.button("Generate Interaction Network"):
            if not os.path.exists(projectdir):
                os.makedirs(projectdir)

            with st.spinner("Creating interaction network..."):

                G = InteractionNetwork()
                G.build_network(pandas_dataframe=df,
                                language_filter=langselector_iso,
                                interaction_type=interaction_type,
                                starttime=ts0,
                                endtime=ts1)
                G.reduce_network(giant_component=True,
                                 aggregation=aggregationmethod,
                                 hard_agg_threshold=hard_aggregation_threshold,                                 
                                 )
                with st.spinner("Computing communities..."):
                    G.community_detection(louvain=rtn_louvain,leiden=rtn_leiden)
                G.build_d3dict(private=privacy,
                               search_query=subtitle,
                               collected_on=collectedon)

            with st.spinner("Writing html..."):
                if langselector != None and langselector != []:
                    if os.name == 'nt': # windows does not accept "|" in filenames
                        language_savesuffix = str(langselector_iso).replace("[","").replace("]","").replace(",","-").replace(" ","").replace("'","")
                    else:
                        language_savesuffix = str(langselector_iso).replace("[","").replace("]","").replace(",","|").replace(" ","").replace("'","")
                    savename = f"{projectdir}/{project}_{interaction_type}network_{language_savesuffix}"
                    savename_export = f"{interaction_type}network_{language_savesuffix}"
                else:
                    savename = f"{projectdir}/{project}_{interaction_type}network"
                    savename_export = f"{interaction_type}network"
                G.write_html(f"{savename}.html")
                st.success(f"`Saved the interactive {interaction_type} network to: {savename}.html`.")

            if rtn_export == True:
                exportpath = f"{projectdir}/export/"
                if not os.path.exists(exportpath):
                    os.makedirs(exportpath)                
                export_graph(G._graph, exportpath + project + savename_export)
                st.success(f"`Exported the network as gml (.gml), edgelist (.csv) and\
                           dot (.gv) to the export folder.`")

            N_edges = len(G._d3dict["links"])

            if N_edges > 1e5:
                st.warning("The network you are trying to visualize has \
                          more than 10,000 links. Consider using a stronger\
                          aggregation method if the interactive visualization is\
                          unresponsive.")
            
    with st.expander("HASHTAG NETWORK"):
        st.write("Undirected network in which nodes are hashtags. \
                  A link is drawn between `i` and `j` if they appear in the same tweet.")
        st.write('<span style="text-decoration: underline;">Options</span>', 
                 unsafe_allow_html=True)
        htn_giantcomponent = st.checkbox("Giant component", key='htn_giantcomponent', help="Reduce the network to its largest connected component.")
        htn_export = st.checkbox("Export the graph to GML, GV and Edgelist",key="htn_export")
        node_thresh_htn = 0
        link_thresh_htn = 0
        node_thresh_htn = st.slider("Remove hashtags that appear less than x times", 
                                    0, 100, 1, 1, 
                                    key='n_thresh_htn')
        link_thresh_htn = st.slider("Remove edges that link hashtags less than than x times", 
                                    0, 50, 1, 1, 
                                    key='l_thresh_htn')
        ht_to_remove = st.text_input(label="Hashtags to be removed from the graph, separated by '|'",
                                     help="It is recommended to remove the hashtag used for the query.")
        if ht_to_remove != "":
            ht_to_remove_list = ht_to_remove.split("|")
        else:
            ht_to_remove_list = None
        st.write('<span style="text-decoration: underline;">Community detection</span>', 
                 unsafe_allow_html=True)
        htn_louvain = st.checkbox("Louvain", key='htn_louvain', help="Requires the installation of the 'louvain' package, currently not working on M1 machines.")
        htn_leiden = st.checkbox("Leiden", key='htn_leiden')


        if st.button("Generate Hashtag Network"):
            if not os.path.exists(projectdir):
                os.makedirs(projectdir)
            with st.spinner("Creating hashtag network..."):
                H = SemanticNetwork()
                ## build a network from the data
                H.build_network(pandas_dataframe=df,
                                language_filter=langselector_iso,
                                hashtags_to_remove=ht_to_remove_list,
                                starttime=ts0,
                                endtime=ts1,
                                             )
                H.reduce_network(giant_component=htn_giantcomponent,
                                 node_threshold=node_thresh_htn,
                                 link_threshold=link_thresh_htn)
                with st.spinner("Computing communities..."):
                    H.community_detection(louvain=htn_louvain,leiden=htn_leiden)
                H.build_d3dict(search_query=subtitle,
                               collected_on=collectedon)

            if langselector != [] and langselector != None:
                if os.name == 'nt': # windows does not accept "|" in filenames
                    language_savesuffix = str(langselector_iso).replace("[","").replace("]","").replace(",","-").replace(" ","").replace("'","")
                else:
                    language_savesuffix = str(langselector_iso).replace("[","").replace("]","").replace(",","|").replace(" ","").replace("'","")
                savename = f"{projectdir}/{project}_nt{node_thresh_htn}_lt{link_thresh_htn}_HTN_{language_savesuffix}"
                exportname = f"{projectdir}/export/{project}_nt{node_thresh_htn}_lt{link_thresh_htn}_HTN_{language_savesuffix}"
            else:
                savename = f"{projectdir}/{project}_nt{node_thresh_htn}_lt{link_thresh_htn}_HTN"
                exportname = f"{projectdir}/export/{project}_nt{node_thresh_htn}_lt{link_thresh_htn}_HTN"                
            
            with st.spinner("Writing html..."):
                st.success(f"`Saved the interactive hashtag network as to: {savename}.html`.")
                H.write_html(savename + ".html")

            if htn_export:
                exportdir = f"{projectdir}/export/"
                if not os.path.exists(exportdir):
                    os.makedirs(exportdir)
                convert_graph(H, exportname)
                st.success(f"`Exported the network as graphml (.gml), edgelist (.csv) and\
                           dot (.gv) to: \n {exportname}`.")

