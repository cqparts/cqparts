#!/usr/bin/env bash
source ./common-vars.sh

case "$1" in
    "")
        # Run tests in interactive mode
        docker run --rm --volume ${CQPARTS_ROOT}:/code -it ${IMAGE}
        ;;
    non-interactive)
        # Run tests (non-interactive; for continuous integration)
        docker run --rm --volume ${CQPARTS_ROOT}:/code ${IMAGE}
        ;;
    *)
        docker run --rm --volume ${CQPARTS_ROOT}:/code -it ${IMAGE} "${@:1}"
        ;;
esac
