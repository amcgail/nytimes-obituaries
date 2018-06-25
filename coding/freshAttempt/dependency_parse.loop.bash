#!/bin/bash

for i in $(seq 0 1)
do
python3 dependency_parse.py $i
done
