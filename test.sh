#!/bin/bash
set -e
rm -rf build raw
python simulate.py
sirad process -n 2
sirad research
python scatterplot.py
