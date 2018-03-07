#!/usr/bin/env bash

cat << EOF
Environment Variables:
    ftp_proxy    = ${ftp_proxy}
    http_proxy   = ${http_proxy}
    https_proxy  = ${https_proxy}
    tester_name  = ${tester_name}
    env_rel_path = ${env_rel_path}
EOF

# install 'add-apt-repository' utility
apt-get update
apt-get install -y software-properties-common

# add FreeCAD apt repo'
add-apt-repository -y ppa:freecad-maintainers/freecad-stable

# 2nd rount installations
apt-get update
apt-get install -y freecad python python-pip
pip install --upgrade pip

# install pip packages
pip install ipython
