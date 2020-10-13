[![twitter explorer][title-img]][title-url]<br/>
[![version][version-img]][version-url]
[![python-version][python-img]][python-url]
[![license][license-img]][license-url]

An interface to explore Twitter data through interactive network visualizations.

## Features

The **twitter explorer** helps computational social scientists to:

- *Collect* Twitter data by providing a visual interface for the Twitter Search API.

- *Transform* the collected data into networks: retweet networks capturing the interaction between users and hashtag networks revealing the semantic layer of the debate. 

- *Explore* these networks interactively by using state-of-the-art network visualizations. 

## Quick start
The **twitter explorer** requires Python ≥ 3.6. If you meet this requirement, open a terminal in your preferred folder to clone the repo and install the required libraries:
```
$ git clone https://github.com/pournaki/twitter-explorer.git
$ pip3 install -r requirements.txt
```
You can now run the collector and the visualizer:
```
$ streamlit run collector.py
$ streamlit run visualizer.py
```
They will open in a new window and instructions will follow.

## Getting started
Please refer to the [documentation](./doc/DOCUMENTATION.md) for detailed installation instructions and how to use the **twitter explorer**.

## Screenshots
![explorer][explorer-img]<br/>

## Data protection
The **twitter explorer** facilitates the collection of data through the Twitter Search API. Please respect the [developer agreement](https://developer.twitter.com/en/developer-terms/agreement-and-policy) when handling the collected data. Our interface includes a privacy option that allows to remove all accessible metadata of users that have less than 5000 followers (no public figures) from the interactive visualization in order to comply with current privacy standards. By only displaying tweets that still exist at the time of exploration, the interface complies with [Twitter's display requirements](https://developer.twitter.com/en/developer-terms/display-requirements). 

## Future development
- Add progress bar for collector
- Incorporate dynamics of the retweet networks
- Add different graph measures

## Common errors
**Error:** `StreamlitAPIException` due to an outdated version of Streamlit  
**Fix:** `pip3 install streamlit --upgrade`

**Error:** `AttributeError: module 'google.protobuf.descriptor' has no attribute '_internal_create_key'`  
**Fix:** `pip3 install protobuf --upgrade`

## How to cite
Please cite our paper if you use the **twitter explorer** in your research:  
Pournaki, A., Gaisbauer, F., Banisch, S., Olbrich, E., The twitter explorer: a framework for observing Twitter through interactive networks.

## Related software
- [DMI-TCAT](https://github.com/digitalmethodsinitiative/dmi-tcat)  
  A powerful tool for streaming real-time tweets and storing them in an SQL database
  
- [twarc](https://github.com/DocNow/twarc)  
  A CLI for Twitter search/streaming API

## About 
The idea for the twitter explorer originated from fruitful discussions in the context of the [Odycceus](https://odycceus.eu) project between [Armin Pournaki](https://pournaki.com), [Felix Gaisbauer](https://www.researchgate.net/profile/Felix_Gaisbauer2), [Sven Banisch](http://universecity.de) and [Eckehard Olbrich](https://www.mis.mpg.de/jjost/members/eckehard-olbrich.html). The tool is designed and developed by Armin Pournaki. 

## Acknowledgements

The **twitter explorer** stands on the shoulders of giants:
- [Streamlit](https://www.streamlit.io/)  
  The frontends of the collector and visualizer are made with Streamlit, a powerful and easily accessible tool to create interactive Python applications.
- [force-graph](https://github.com/vasturiano/force-graph)  
  The interactive graph visualization relies on the force-graph library.
- [igraph](https://igraph.org/python/)  
  All the graph operations in the **twitter explorer** are handled by the Python version of igraph.
- [tweepy](http://www.tweepy.org/)  
  An easy-to-use Python wrapper for Twitter API.

## Funding
This project has received funding from the European Union’s Horizon 2020 research and innovation programme under grant agreement No 732942.

## License
The **twitter explorer** is licensed under the [GNU GPLV3](https://www.gnu.org/licenses/gpl-3.0.en.html) license.

<!-- logos and links -->
[title-img]: ./doc/img/titlelogo.png
[title-url]: https://twitterexplorer.org
[version-img]:https://img.shields.io/badge/version-0.3-000?style=for-the-badge&?color=ffffff&?logoWidth=100
[version-url]:https://twitterexplorer.org
[python-img]:https://img.shields.io/badge/python-%E2%89%A53.6-000?style=for-the-badge&?color=ffffff
[python-url]:https://www.python.org/downloads/release/python-360/
[license-img]:https://img.shields.io/badge/license-GNU%20GPLv3-000?style=for-the-badge&?color=ffffff
[license-url]:https://www.gnu.org/licenses/gpl-3.0.en.html
[explorer-img]:./doc/img/explorer.png
