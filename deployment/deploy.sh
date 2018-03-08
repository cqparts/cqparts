
# constants
CONTAINER_NAME=deploytest

CQPARTS_ROOT=$(git rev-parse --show-toplevel)


function show_help() {
    [ "$@" ] && echo "$@"
cat << EOF
Usage: ./${0##*/} {build|test|and so on ...}

This script is to maintain a consistent method of deployment and testing.

Arguments:
    Setup:
        setup       Installs packages & sets up environment (requires sudo)

    Compiling:
        build {lib} Execute setup to build packages (populates ../dist/)
                    creates both 'sdist' and 'wheel' distrobutions.
        clean       Removes 'build', 'dist', and 'src' folders

    Docker Environments: (always named $CONTAINER_NAME)
        env new {env}       Create new container, remove old
        env ls              List container
        env rm              Remove container
        env prereq {lib}    Install pre-requisites for given lib

    Deploy:
        deploy {lib} (test|prod)  Upload to PyPi server

    Install:
        install sdist    {lib}  Install from local sdist
        install wheel    {lib}  Install from local wheel
        install pypitest {lib}  Install from PyPi test server
        install pypi     {lib}  Install from PyPi (official)

    Testing:
        test {lib}          Run unittests for the given lib

    Help:
        -h | --help     display this message

Libraries Available for Deployment: {lib}
EOF
find ../src -maxdepth 1 -type d -printf "    %P\n" | sort | grep -vP '^(.*\.egg-info|\s*)$'
cat << EOF

Environments: {env}
EOF
find env -maxdepth 1 -type d -printf "    %P\n" | sort | grep -vP '^\s*$'

}

# --------- Utilities ---------

function lib_ver() {
    # Get library vesion number
    _lib=$1
    pushd ../src > /dev/null
    python -c "import ${_lib}; print('VERSIONKEY'+${_lib}.__version__)" | grep VERSIONKEY | sed -e 's/^VERSIONKEY//'
    popd > /dev/null
}


# --------- Setup ---------
# setting up host OS with the tools needed to build
# I'm assuming the same machine has been used to modify and test code,
# in which case the host OS will already have:
#   - python, pip
#   - docker

function setup() {
    sudo pip install -U -r requirements.txt
}


# --------- Build ---------

function clean() {
    test -d build && rm -rfv build
    test -d dist && rm -rfv dist
    test -d src && rm -rfv src
}

function build() {
    _lib=$1
    if [ -n "$_lib" -a -d ${CQPARTS_ROOT}/src/${_lib} ] ; then
        test -d build && rm -rf build  # fresh build
        python setup.py --lib ${_lib} sdist bdist_wheel
    else
        echo "ERROR: no library named ${_lib}" >&2
        show_help >&2 ; exit 1
    fi
}


# --------- Docker Environment ---------

function env_new() {
    # Start with a fresh (unmodified) container
    _env=$1
    if [ -z "${_env}" ] ; then
        show_help >&2 ; exit 1
    else
        # remove existing container
        env_rm
        # start a new container, with a blocking bash prompt (detatched)
        docker run \
            -it -d \
            --name ${CONTAINER_NAME} \
            --volume ${CQPARTS_ROOT}:/code \
            cqparts-deploytest:${_env} \
            bash
    fi
}

function env_ls() {
    docker ps --format "{{.Image}} -- {{.Names}}" -f name=${CONTAINER_NAME}
}

function env_rm() {
    # remove container (if it exists to delete)
    if [ -n "$(docker ps -aqf name=${CONTAINER_NAME})" ] ; then
        docker rm -f ${CONTAINER_NAME}
    fi
}

function env_prereq() {
    # install python pre-requisites for the given library
    _lib=$1
    if [ -e ${CQPARTS_ROOT}/src/${_lib}/requirements.txt ] ; then
        docker exec -u root ${CONTAINER_NAME} bash -c \
            "\${PIP_BIN} install -r /code/src/${_lib}/requirements.txt"
    fi
}

function env_bash() {
    # Open a bash shell on the test environment container
    docker exec -it -u root ${CONTAINER_NAME} bash ${@:1}
}


# --------- Deploy ---------
function deploy() {
    # deploy to the given server (test|prod)
    _lib=$1
    _srv=$2

    _lib_ver=$(lib_ver ${_lib})

    if [ -n "${_srv}" ] ; then
        twine upload -r ${_srv} dist/${_lib}-${_lib_ver}*
    fi
}


# --------- Install ---------
# Install built or deployed library into test environment (in preparation
# for testing)
function install_sdist() {
    _lib=$1
    _lib_ver=$(lib_ver ${_lib})

    docker exec \
        --user root \
        --workdir "/code/deployment" \
        ${CONTAINER_NAME} \
        bash -c "\${PIP_BIN} install dist/${_lib}-${_lib_ver}.tar.gz"
}

function install_wheel() {
    _lib=$1
    # TODO
    echo not implemented
}

function install_pypitest() {
    _lib=$1
    # TODO
    echo not implemented
}

function install_pypi() {
    _lib=$1
    # TODO
    echo not implemented
}


# --------- Testing ---------

function run_tests() {
    _lib=$1
    # TODO
    echo not implemented
}


# --------- Mainline ---------

case "$1" in
    # Show help on request
    -h|--help) show_help ; exit 0 ;;

    # Valid Actions
    setup) setup ${@:2} ;;
    build) build ${@:2} ;;
    clean) clean ${@:2} ;;
    env)
        case "$2" in
            ls) env_ls ${@:3} ;;
            rm) env_rm ${@:3} ;;
            new) env_new ${@:3} ;;
            prereq) env_prereq ${@:3} ;;
            bash) env_bash ${@:3} ;;
            *) show_help >&2 ; exit 1 ;;
        esac ;;
    deploy) deploy ${@:2} ;;
    install)
        case "$2" in
            sdist) install_sdist ${@:3} ;;
            wheel) install_wheel ${@:3} ;;
            pypitest) install_pypitest ${@:3} ;;
            pypi) install_pypi ${@:3} ;;
        esac ;;
    test) run_tests ${@:2} ;;

    # otherwise... show help
    *) show_help >&2 ; exit 1 ;;
esac
