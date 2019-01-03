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

# install from custom-packages folder
find /code/tests/env/custom-packages \
    -name *.tar.gz \
    -exec pip3 install {} \;

# install requirements for each library in 'src' sub-folders
req_pkgs=$( \
    find /code/src \
        -mindepth 2 -maxdepth 2 \
        -name requirements.txt \
        -exec cat {} \; | uniq | grep -vP "^cqparts$"
)
pip3 install ${req_pkgs}

# install test requirements
pip3 install -r /code/tests/requirements.txt

# install cadquery : pythonocc
function install_cadquery_pythonocc() {
    temp_folder=/tmp/cadquery ; mkdir -p ${temp_folder}
    branch=master
    dest=/opt/python-lib ; mkdir -p ${dest}

    pushd ${temp_folder}
    wget https://api.github.com/repos/CadQuery/cadquery/tarball/${branch} -O cq.tar.gz
    root_folder=$(tar --exclude='*/*' -tf cq.tar.gz)
    tar -xvf cq.tar.gz ${root_folder}cadquery
    mv ${root_folder}/cadquery ${dest}/cadquery
    popd

    rm -rf ${temp_folder}
}

install_cadquery_pythonocc
