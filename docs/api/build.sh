#!/usr/bin/env bash

# This directory (the folder this script is in)
DIR=$(dirname $0)

sphinx-apidoc $* -o ${DIR} ${DIR}/../../src/cqparts
