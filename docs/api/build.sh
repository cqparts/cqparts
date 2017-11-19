#!/usr/bin/env bash

# This directory (the folder this script is in)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

sphinx-apidoc $* -o ${DIR} ${DIR}/../../src/cqparts
