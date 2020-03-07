[![twitter explorer][title-img]][title-url]<br/>

Table of Contents
=================

   * [Table of Contents](#table-of-contents)
   * [Introduction](#introduction)
   * [Installation](#installation)
      * [Unix / macOS](#unix--macos)
      * [Windows](#windows)
   * [Data collection](#data-collection)
      * [Authentication](#authentication)
      * [Collecting tweets](#collecting-tweets)
   * [Data transformation](#data-transformation)
      * [Timeline of tweets](#timeline-of-tweets)
      * [Retweet networks](#retweet-networks)
         * [Giant Component](#giant-component)
         * [Aggregation methods](#aggregation-methods)
         * [Privacy option](#privacy-option)
         * [Community detection](#community-detection)
      * [Hashtag networks](#hashtag-networks)
         * [Giant Component](#giant-component-1)
         * [Community detection](#community-detection-1)
      * [Clustergraphs](#clustergraphs)
      * [Export options](#export-options)
      * [File structure](#file-structure)
   * [Network exploration](#network-exploration)
   * [References](#references)

# Introduction

[![twitter explorer][arch-img]][title-url]<br/>

The **twitter explorer** is an open framework that consists of three components: 
The *collector* (left), after having set up the credentials, allows for connection to the Twitter Search API and saves the collected tweets in `jsonl` format. They are then passed on to the *visualizer* (middle), where the user can get an overview of the content and then create retweet and hashtag networks. The interactive networks are generated as html files that can be explored in the web browser. The modular structure of the three components facilitates the development of new features which are suggested by the light grey boxes.

# Installation

## Unix / macOS
The **twitter explorer** requires Python ≥ 3.6 to run. You most likely already have Python installed. To check which Python version you have, open a terminal window and type:
```
python -V
```
If your version is above 3.6, continue to the next step. Otherwise, please refer to the guides specific to your operating system to install Python ≥ 3.6. 

Download the current release of the **twitter explorer**. Open a terminal again and change to the folder to which you downloaded the **twitter explorer**. Now run the following command to install the necessary libraries:
```
pip3 install -r requirements.txt
```

## Windows
We recommend Windows users to install [Anaconda Python](https://www.anaconda.com/distribution/#download-section). Follow the installation instructions on the website to install it. 

Then download the current release of the **twitter explorer**. Go to the folder where you downloaded it and right-click and `Open Powershell here`. Now type in the following command to install the necessary packages:
```
conda install streamlit tweepy pandas cufflinks plotly json-lines python-igraph louvain
```
Once `conda` has finished installing the packages you are ready to start the **twitter explorer**.

# Data collection

## Authentication
To use the **twitter explorer**, you need to apply for a [Twitter Developer Account](https://developer.twitter.com/en/use-cases/academic-researchers). Follow the steps on the link to create a new research account or to transform an existing account into one. Now, go to the [Apps section](https://developer.twitter.com/en/apps) of your Twitter account and click on `Create an app` in the upper right corner:


![createapp][createapp]


Enter `twitter explorer` as the name and a description of the research you want to do with the tool in the description field. As website enter `twitterexplorer.org`. In the last field, enter `Explore Twitter data through network representations`. Now create the app with the `create` button.

Go to your new app and enter the `Keys and tokens` section. Copy the Consumer API keys:
![apikeys][apikeys]


Create a new file in the **twitter explorer** folder called `twitter_apikeys.txt` with the following content:
```
# api_key
<insert api_key here>
# api_secret_key
<insert api_secret_key here>
```
The **twitter explorer** is now ready to connect to the API using [OAuth 2.0](https://developer.twitter.com/en/docs/basics/authentication/oauth-2-0/application-only).

## Collecting tweets
The collector connects to the [Twitter Search API](https://developer.twitter.com/en/docs/tweets/search/api-reference/get-search-tweets), which allows users to collect tweets from the last 7 days based on an advanced search. Please refer to @igorbrigadir's [documentation](https://github.com/igorbrigadir/twitter-advanced-search) of the Twitter Advanced Search or [try it out](https://twitter.com/search-advanced) in the browser to get a feeling for the possible options.

Change to the folder where you downloaded streamlit, open a terminal and start the data collector by typing:
```
streamlit run collector.py
```
The collector interface will open in your browser. You can start a search based on a keyword. The tweets will be downloaded and continuously written into a new [json-lines](http://jsonlines.org/) file in `./data/{currentdate_keyword.jsonl}`. Each line of this file contains one tweet object. Note that there are [rate limits](https://developer.twitter.com/en/docs/basics/rate-limiting) in the free Search API. When the **twitter explorer** reaches a rate limit, it will sleep for 15mins and continue the search afterwards. From experience, this results to ~7500 tweets per 15mins. 
Also, keep in mind the following statement about the Twitter Search API:
> Please note that Twitter's search service and, by extension, the Search API is not meant to be an exhaustive source of Tweets. Not all Tweets will be indexed or made available via the search interface.

# Data transformation
Start the visualizer, which will open the second interface in a browser window:
```
streamlit run visualizer.py
```
You can select a previously collected dataset for further analysis from a drop-down menu. If you have your own Twitter dataset, please convert it to the `json-lines` format (every tweet dictionary in one line) and copy it to the `./data` folder. 

The visualizer will create a new folder for every collection you make in the `output` folder. Refer to [File structure](#file-structure) for a detailed list of files generated by the **twitter explorer**.

## Timeline of tweets
As a first step, the visualizer creates a timeseries showing the amount of tweets in the dataset over time, which will be saved in the project folder. 

## Retweet networks
The **twitter explorer** can generate retweet networks in which nodes are users. A link is drawn from node `i` to `j` if `i` retweets `j`. The following methods are available:

### Giant Component
When enabled, the graph will be reduced to its largest connected component. 

### Aggregation methods
- "Soft" aggregation
  Removes all users that are never retweeted and only retweet one other user (and can therefore not be bridges in the network)
  
- "Hard" aggregation
  Removes all users from the network that are retweeted less than `t` times.

### Privacy option
Removes all accessible metadata of users that have less than 5000 followers (no public figures) from the interactive visualization in order to comply with current privacy standards. The nodes are visible and their links are taken into account, but they cannot be personally identified in the interface.

### Community detection
The **twitter explorer** currently supports Louvain [[1]](#louvain) and InfoMap [[2]](#infomap) algorithms for community detection. The community assignments are saved as node metadata. Note that the Louvain community detection does not take into account link direction.

## Hashtag networks
The **twitter explorer** can generate hashtag networks in which nodes are hashtags. A link is drawn between node `i` and `j` if `i` and `j` appear in the same tweet. The following methods are available:

### Giant Component
When enabled, the graph will be reduced to its largest connected component. 

### Community detection
The **twitter explorer** currently supports Louvain [[1]](#louvain) community detection for hashtag networks.

## Clustergraphs
If community detection is enabled, clustergraphs will be generated for both retweet and hashtag networks in which nodes are communities and links are weighted according the the cumulative links between users of the communities.

## Export options
![context][context]<br/>

Its modular structure (division into collector/visualizer/explorer) and the ability to export the data makes the tool compatible with a variety of other data analysis tools. Both retweet and hashtag networks are saved as edgelist (`.csv`), GML (`.gml`) and GraphViz Dot (`.gv`).

## File structure
A summary of the file structure is found below: 

```
COLLECTED DATA (created by the collector)
.data/
.data/{date}_tweets_{keyword}.jsonl <-- collected dataset

INTERACTIVE NETWORKS (created by the visualizer)
./output/

./output/{date}_{keyword}/{date}_{keyword}_timeline.html <-- timeline of tweets

./output/{date}_{keyword}/{date}_{keyword}_RTN.html <-- retweet network
./output/{date}_{keyword}/{date}_{keyword}_HTN.html <-- hashtag network
./output/{date}_{keyword}/{date}_{keyword}_RTN_CG_{comdec_method}.html <-- retweet network clustergraph
./output/{date}_{keyword}/{date}_{keyword}_HTN_CG_{comdec_method}.html <-- hashtag network clustergraph

EXPORTED NETWORKS (created by the visualizer)
./output/{date}_{keyword}/export/
./output/{date}_{keyword}/export/RTN.csv <-- retweet network as edgelist
./output/{date}_{keyword}/export/RTN.gml <-- retweet network as gml
./output/{date}_{keyword}/export/RTN.gv  <-- retweet network as dot for graphviz
./output/{date}_{keyword}/export/HTN.csv <-- hashtag network as edgelist
./output/{date}_{keyword}/export/HTN.gml <-- hashtag network as gml
./output/{date}_{keyword}/export/HTN.gv  <-- hashtag network as dot for graphviz
```

# Network exploration
![explorer_screenshot][explorer-img]<br/>
Open the generated `html` files to explore the generated networks (we recommend using the latest version of Firefox for full feature support). The command palette on the left displays information about the network and can be interacted with. Currently, the following features are implemented:
- show information about the dataset
- show number of nodes and links
- recolor nodes according to community assignment
- change node size according to metadata values
- change node scaling (experimental)
- display user metadata on click
- search for users / hashtags
- show user tweets in dataset
- show current user timeline

# References
<a name="louvain">[1]</a> Blondel, Vincent D., et al. "Fast unfolding of communities in large networks." Journal of statistical mechanics: theory and experiment 2008.10 (2008): P10008.  
<a name="infomap">[2]</a> Rosvall, Martin, Daniel Axelsson, and Carl T. Bergstrom. "The map equation." The European Physical Journal Special Topics 178.1 (2009): 13-23.  

[title-img]: ./img/doc.png
[title-url]: https://twitterexplorer.org
[arch-img]: ./img/architecture.png
[explorer-img]: ./img/explorer.png
[createapp]: ./img/createapp.png
[apikeys]: ./img/apikeys.png
[context]: ./img/context.png
