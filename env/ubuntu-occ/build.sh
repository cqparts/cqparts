#!/usr/bin/env bash
source ./common-vars.sh

ENV_REL_PATH=$(python -c "import os.path; print(os.path.relpath('${PWD}', '${CQPARTS_ROOT}'))")

# work from repository root
pushd ${CQPARTS_ROOT}

docker build \
    --tag ${IMAGE} \
    --build-arg ftp_proxy=${ftp_proxy} \
    --build-arg http_proxy=${http_proxy} \
    --build-arg https_proxy=${https_proxy} \
    --build-arg env_rel_path=${ENV_REL_PATH} \
    --file ${ENV_REL_PATH}/Dockerfile \
    .

popd
