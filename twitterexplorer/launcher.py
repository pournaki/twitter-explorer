#!/usr/bin/env python
## =============================================================================
## twitter explorer
## webapp runner
## =============================================================================

import os
import sys
from argparse import ArgumentParser
from streamlit.web import cli as stcli

def main():
    ap = ArgumentParser()
    ap.add_argument('app', type=str)
    args = ap.parse_args()
    torun = args.app

    filepath = os.path.realpath(os.path.dirname(__file__))

    if torun == "visualizer":
        pathtorun = filepath + "/apps/" + "visualizer.py"
    elif torun == "collector":
        pathtorun = filepath + "/apps/" + "collector.py"
    
    sys.argv = ["streamlit", "run", pathtorun]
    sys.exit(stcli.main())