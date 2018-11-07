#!/usr/bin/env bash

set -e

cat << EOF
Environment Variables:
    ftp_proxy    = ${ftp_proxy}
    http_proxy   = ${http_proxy}
    https_proxy  = ${https_proxy}
    tester_name  = ${tester_name}
    env_rel_path = ${env_rel_path}
EOF

# Install apt packages
apt-get update
apt-get install -y python3 python3-pip wget libglu1-mesa jq
python3 -m pip install --upgrade pip

# using conda package management to install cadquery-occ
wget -nv https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh
bash /tmp/miniconda.sh -b -p /opt/miniconda
export PATH="$PATH:/opt/miniconda/bin"
hash -r
conda config --set always_yes yes --set changeps1 no
conda update conda
conda install -c pythonocc -c oce -c conda-forge -c dlr-sc -c CadQuery cadquery-occ

# Make a symlink at /conda_packages that points to conda's site-packages dir so
# we can add it to PYTHONPATH. Ideally this would be done with docker's ENV, but
# ENV only handles static values. See https://github.com/moby/moby/issues/29110.
CONDA_PKGS="$(dirname $(conda info --json | jq .conda_location --raw-output))"
ln -s "$CONDA_PKGS" /conda_packages

# install pip packages
python3 -m pip install ipython
