#!/usr/bin/env bash
source ./common-vars.sh

case "$1" in
    tests|"")
        docker run --rm --volume ${CQPARTS_ROOT}:/code ${IMAGE}
        ;;
    *)
        docker run \
            --rm -it \
            --volume ${CQPARTS_ROOT}:/code \
            -p 9041:9041 \
            ${IMAGE} "${@:1}"
        ;;
esac
