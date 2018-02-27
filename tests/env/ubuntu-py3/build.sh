#!/usr/bin/env bash

LOCAL=${PWD}
CQPARTS_ROOT=$(git rev-parse --show-toplevel)
ENV_REL_PATH=$(python -c "import os.path; print(os.path.relpath('${LOCAL}', '${CQPARTS_ROOT}'))")
ENV_NAME=${PWD##*/}

# work from repository root
pushd ${CQPARTS_ROOT}

docker build \
    --tag cqparts-test:${ENV_NAME} \
    --build-arg ftp_proxy=${ftp_proxy} \
    --build-arg http_proxy=${http_proxy} \
    --build-arg https_proxy=${https_proxy} \
    --build-arg env_rel_path=${ENV_REL_PATH} \
    --file ${ENV_REL_PATH}/Dockerfile \
    .

popd
