#!/usr/bin/env bash
source ./common-vars.sh

function run_container() {
    docker run --rm \
        --name ${IMAGE_BASE} \
        --volume ${CQPARTS_ROOT}:/code \
        --publish 9041:9041 \
        -it ${IMAGE} "$@"
}

case "$1" in
    "")
        # Run tests in interactive mode
        run_container
        ;;
    non-interactive)
        # Run tests (non-interactive; for continuous integration)
        docker run --rm --volume ${CQPARTS_ROOT}:/code ${IMAGE}
        ;;
    core)
        # Only run core t_cqparts tests
        run_container python3 runtests.py --module cqparts
        ;;
    *)
        run_container "${@:1}"
        ;;
esac
