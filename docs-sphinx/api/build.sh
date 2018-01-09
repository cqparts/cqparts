#!/usr/bin/env bash

# This directory (the folder this script is in)
DIR=$(dirname $0)

rm ${DIR}/*.rst
sphinx-apidoc $* -o ${DIR} ${DIR}/../../src

# Replace title in modules file (extend underline)
title="Module APIs"
index_file=${DIR}/modules.rst

sed -i "1s/.*/${title}/" ${index_file}
sed -i "2s/.*/=============================/" ${index_file}
