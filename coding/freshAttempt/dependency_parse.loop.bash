#!/bin/bash

for i in $(seq 2 6)
do
python3 dependency_parse.py $i
done
