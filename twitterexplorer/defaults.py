## =============================================================================
## twitter explorer 
## defaults
## =============================================================================

import os
home = os.path.expanduser('~')
DEFAULT_DATA_DIR = home + "/twitterexplorer/data/"
DEFAULT_OUTPUT_DIR = home + "/twitterexplorer/output/"
DEFAULT_API_KEY_PATH_V2 = home + "/twitterexplorer/twitter_bearertoken.txt"
DEFAULT_API_KEY_PATH_V1 = home + "/twitterexplorer/twitter_apikeys.txt"
PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))