#!/usr/bin/env bash

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
    -exec pip install {} \;

# install requirements for each library in 'src' sub-folders
req_pkgs=$( \
    find /code/src \
        -mindepth 2 -maxdepth 2 \
        -name requirements.txt \
        -exec cat {} \; | uniq | grep -vP "^cqparts$"
)
pip install ${req_pkgs}

# install test requirements
pip install -r /code/tests/requirements.txt
