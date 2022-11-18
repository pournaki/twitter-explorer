## =============================================================================
## twitter explorer visualizer
## =============================================================================

import os
import pandas as pd
import numpy as np
import altair as alt
import streamlit as st
import datetime as dt

from twitterexplorer.legacy import *
from twitterexplorer.helpers import *
from twitterexplorer.streamlitutils import *
from twitterexplorer.plotters import *
from twitterexplorer.communitydetection import *
from twitterexplorer.networks import *
from twitterexplorer.d3networks import *
from twitterexplorer.converters import twitterjsonl_to_twitwicsv
from twitterexplorer.config import version_number

ui_changes()

st.title("Visualizer")

filename = file_selector('./data')

if filename not in ["./data/---","./data\\---"]:

    filesize = os.path.getsize(filename) >> 20

    if filename[-1] == "l":
        subtitlevalue = filename[25:][:-6]
    else:
        subtitlevalue = filename[25:][:-4]

    collectedon = filename[7:17]
    subtitle = subtitlevalue
    project = st.text_input(label="Set a foldername for the project that will be \
        created in ./output",
                            value=f"{collectedon}_{subtitle}")

    st.write(f'`You selected {filename}.`<br>\
        `The file size is about {filesize}MB.`', unsafe_allow_html=True)

    datadir = "./data/"
    outputdir = "./output/"
    projectdir = outputdir + project

    @st.cache
    def load_data(path):
        ## pandas does strange things to IDs, like importing them as ints and using
        ## scientific notation, so we need to make sure they are read as strings
        try:
            df = pd.read_csv(path,
                             dtype={"id":str,
                                    "user_id":str,
                                    "to_userid":str,
                                    "to_tweetid":str,
                                    "retweeted_id":str,
                                    "retweeted_user_id":str,
                                    "quoted_id":str,
                                    "quoted_user_id":str,
                                    "mentioned_ids":str,
                                    "mentioned_names":str,
                                    "hashtags":str,
                                    "timestamp_utc":int,
                                    },
                            low_memory=False,
                            # lineterminator='\n'
                         )
        except (pd.errors.ParserError,ValueError) as e:
        ## https://stackoverflow.com/a/48187106
            df = pd.read_csv(path,
                             dtype={"id":str,
                                    "user_id":str,
                                    "to_userid":str,
                                    "to_tweetid":str,
                                    "retweeted_id":str,
                                    "retweeted_user_id":str,
                                    "quoted_id":str,
                                    "quoted_user_id":str,
                                    "mentioned_ids":str,
                                    "mentioned_names":str,
                                    "hashtags":str,
                                    "timestamp_utc":int
                                    },
                            low_memory=False,
                            lineterminator='\n'
                         )            
        ## remove possible duplicates, even though the collector
        ## should not collect doubles
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
    
    ## when you convert an old jsonl-format, there is no meaningful
    ## 'collected_via' field    
    try:        
        tweet_count_chart = plot_tweetcounts(groupby_type(df[df['collected_via'].isna()]))
    except ValueError:
        tweet_count_chart = plot_tweetcounts(groupby_type(df))
    st.altair_chart(tweet_count_chart, use_container_width=True)

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

    if st.checkbox("Language filter"):
        with open ('./twitterexplorer/languages.json', 'r', encoding='utf-8') as f:
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
        langselector = "None"
    
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
                if langselector != "None" and langselector != []:
                    G = twitter_df_to_interactionnetwork(df=df[df['lang'].isin(langselector_iso)],
                                                         starttime=ts0,
                                                         endtime=ts1,
                                                         interaction_type=interaction_type)
                else:
                    G = twitter_df_to_interactionnetwork(df=df,
                                                         starttime=ts0,
                                                         endtime=ts1,
                                                         interaction_type=interaction_type)
            # reduce the network
            G = reduce_network(G,
                               giant_component=rtn_giantcomponent,
                               aggregation=aggregationmethod,
                               hard_agg_threshold=hard_aggregation_threshold)

            # get the first and last tweet    
            edgeslist = list(G.es)
            try:
                firstdate_str = str(dt.datetime.fromtimestamp(edgeslist[-1]["timestamp"]))
                lastdate_str = str(dt.datetime.fromtimestamp(edgeslist[0]["timestamp"]))
            except IndexError:
                st.error(f"There seem to be no collected {interaction_type} interactions in the dataset!")
        
            if rtn_louvain == True:
                with st.spinner("Computing Louvain communities..."):
                    G, cgl = compute_louvain(G)        
                    cgl_d3 = d3_cg_rtn(cgl)
                    cgl_d3["graph"] = {}
                    cgl_d3['graph']['type'] = f"{interaction_type.capitalize()} network <br> Louvain graph"
                    cgl_d3['graph']['keyword'] = subtitle
                    cgl_d3['graph']['collected_on'] = collectedon
                    cgl_d3['graph']['first_tweet'] = firstdate_str
                    cgl_d3['graph']['last_tweet'] = lastdate_str
                    cgl_d3['graph']['N_nodes'] = len(cgl_d3["nodes"])
                    cgl_d3['graph']['N_links'] = len(cgl_d3["links"])
                    cgl_d3['version_number'] = version_number
                    x = cg_rtn_html(cgl_d3)
                    with open(f"{projectdir}/{project}_{interaction_type}_CG_louvain.html", "w",
                              encoding='utf-8') as f:
                        f.write(x)

            if rtn_leiden == True:
                with st.spinner("Computing Leiden communities..."):
                    G, cgl = compute_leiden(G)        
                    cgl_d3 = d3_cg_rtn(cgl)
                    cgl_d3["graph"] = {}
                    cgl_d3['graph']['type'] = f"{interaction_type.capitalize()} network <br> Leiden graph"
                    cgl_d3['graph']['keyword'] = subtitle
                    cgl_d3['graph']['collected_on'] = collectedon
                    cgl_d3['graph']['first_tweet'] = firstdate_str
                    cgl_d3['graph']['last_tweet'] = lastdate_str
                    cgl_d3['graph']['N_nodes'] = len(cgl_d3["nodes"])
                    cgl_d3['graph']['N_links'] = len(cgl_d3["links"])
                    cgl_d3['version_number'] = version_number
                    x = cg_rtn_html(cgl_d3)
                    with open(f"{projectdir}/{project}_{interaction_type}_CG_leiden.html", "w",
                              encoding='utf-8') as f:
                        f.write(x)
                
            # create d3-graph and fill it with info
            RTN = d3_rtn(G,private=privacy)
            RTN['graph'] = {}
            RTN['graph']['type'] = f"{interaction_type.capitalize()} network"
            RTN['graph']['N_nodes'] = len(RTN["nodes"])
            RTN['graph']['N_links'] = len(RTN["links"])
            RTN['graph']['keyword'] = subtitle
            RTN['graph']['collected_on'] = collectedon
            RTN['graph']['first_tweet'] = firstdate_str
            RTN['graph']['last_tweet'] = lastdate_str
            RTN['version_number'] = version_number

            if privacy:
                x = rtn_html_p(data=RTN)
            else:
                x = rtn_html(data=RTN)

            with st.spinner("Writing html..."):
                if langselector != "None" and langselector != []:
                    if os.name == 'nt': # windows does not accept "|" in filenames
                        language_savesuffix = str(langselector_iso).replace("[","").replace("]","").replace(",","-").replace(" ","").replace("'","")
                    else:
                        language_savesuffix = str(langselector_iso).replace("[","").replace("]","").replace(",","|").replace(" ","").replace("'","")
                    savename = f"{projectdir}/{project}_{interaction_type}network_{language_savesuffix}"
                    savename_export = f"{interaction_type}network_{language_savesuffix}"
                else:
                    savename = f"{projectdir}/{project}_{interaction_type}network"
                    savename_export = f"{interaction_type}network"
                with open(f"{savename}.html", "w",
                              encoding='utf-8') as f:
                    f.write(x)
            
            exportpath = f"{projectdir}/export/"
            if not os.path.exists(exportpath):
                os.makedirs(exportpath)                
            convert_graph(G, exportpath + project + savename_export)

            N_edges = len(RTN["links"])

            if N_edges > 1e5:
                st.warning("The network you are trying to visualize has \
                          more than 10,000 links. Consider using a stronger\
                          aggregation method if the interactive visualization is\
                          unresponsive.")
            
            st.success(f"`Saved the interactive {interaction_type} network to: {savename}.html`.")
            if rtn_louvain == True:
                st.success(f"`Saved the Louvain cluster graph to: {savename}_CG.html`.")
            st.success(f"`Exported the network as gml (.gml), edgelist (.csv) and\
                       dot (.gv) to the export folder.`")

    with st.expander("HASHTAG NETWORK"):
        st.write("Undirected network in which nodes are hashtags. \
                  A link is drawn between `i` and `j` if they appear in the same tweet.")
        st.write('<span style="text-decoration: underline;">Options</span>', 
                 unsafe_allow_html=True)
        htn_giantcomponent = st.checkbox("Giant component", key='htn_giantcomponent', help="Reduce the network to its largest connected component.")
        node_thresh_htn = 0
        link_thresh_htn = 0
        node_thresh_htn = st.slider("Remove hashtags that appear less than x times", 
                                    0, 100, 1, 1, 
                                    key='n_thresh_htn')
        link_thresh_htn = st.slider("Remove edges that link hashtags less than than x times", 
                                    0, 50, 1, 1, 
                                    key='l_thresh_htn')
        st.write('<span style="text-decoration: underline;">Community detection</span>', 
                 unsafe_allow_html=True)
        htn_louvain = st.checkbox("Louvain", key='htn_louvain', help="Requires the installation of the 'louvain' package, currently not working on M1 machines.")
        htn_leiden = st.checkbox("Leiden", key='htn_leiden')

        if st.button("Generate Hashtag Network"):
            if not os.path.exists(projectdir):
                os.makedirs(projectdir)
            with st.spinner("Creating hashtag network..."):
                if langselector != "None":

                    H = twitter_df_to_hashtagnetwork(df=df[df['lang'].isin(langselector_iso)],
                                                     starttime=ts0,
                                                     endtime=ts1)
                else:
                    H = twitter_df_to_hashtagnetwork(df=df,
                                                     starttime=ts0,
                                                     endtime=ts1)
                H = reduce_semanticnetwork(H,
                                           giant_component=htn_giantcomponent,
                                           node_threshold=node_thresh_htn,
                                           link_threshold=link_thresh_htn)
                if htn_louvain:
                    with st.spinner("Computing communities..."):
                        H, Hcg = compute_louvain(H)
                if htn_leiden:
                    with st.spinner("Computing communities..."):
                        H, Hcg = compute_leiden(H)
            # get the first and last tweet    
            edgeslist = list(H.es)
            firstdate_str = str(dt.datetime.fromtimestamp(edgeslist[-1]["time"]))
            lastdate_str = str(dt.datetime.fromtimestamp(edgeslist[0]["time"]))
            HTN = d3_htn(H)
            HTN['graph'] = {}
            HTN['graph']['type'] = "Hashtag network"
            HTN['graph']['N_nodes'] = len(HTN["nodes"])
            HTN['graph']['N_links'] = len(HTN["links"])
            HTN['graph']['keyword'] = subtitle
            HTN['graph']['collected_on'] = collectedon
            HTN['graph']['first_tweet'] = firstdate_str
            HTN['graph']['last_tweet'] = lastdate_str
            HTN['version_number'] = version_number

            x = htn_html(data=HTN)
            if langselector != "None" and langselector != []:
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
                with open(savename + ".html", "w", encoding='utf-8') as f:
                    f.write(x)                
            exportdir = f"{projectdir}/export/"
            if not os.path.exists(exportdir):
                os.makedirs(exportdir)
            convert_graph(H, exportname)

            st.success(f"`Saved the interactive hashtag network as to: {savename}.html`.")
            st.success(f"`Exported the network as graphml (.gml), edgelist (.csv) and\
                       dot (.gv) to: \n {exportname}`.")
