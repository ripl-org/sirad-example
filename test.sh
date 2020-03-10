#!/bin/bash
set -e
rm -rf build raw
python simulate.py
sirad sources
sirad validate
sirad process
sirad -n 2 process
sirad research
sirad -n 2 research
python scatterplot.py
