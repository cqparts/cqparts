# Library Deployment

For anyone reading, this readme and all files in this folder are mainly just
notes for myself; they have little to do with `cqparts` itself.

However, if you're interested in deploying your own PyPi package, then hopefully
this can help.

Method started with a basis from the articles:

* http://peterdowns.com/posts/first-time-with-pypi.html and
* https://hynek.me/articles/sharing-your-labor-of-love-pypi-quick-and-dirty/

Deployment almost exclusively uses the `./deploy.sh` script in this folder.
At this time, running `./deploy.sh --help` displays:

    Usage: ./deploy.sh {build|test|and so on ...}

    This script is to maintain a consistent method of deployment and testing.

    Arguments:
        Setup:
            setup       Installs packages & sets up environment (requires sudo)

        Compiling:
            build {lib} Generate ../src/setup.py and execute to build packages
            clean       Removes 'build', 'dist', and 'src' folders

        Docker Environments: (always named deploytest)
            env new {env}       Create new container, remove old
            env ls              List container
            env rm              Remove container
            env prereq {lib}    Install pre-requisites for given lib
            env testreq         Install test-specific requirements
            env bash            Run Bash prompt in the container
            env python          Run Python in the container

        Deploy:
            register (test|prod)    Register lib last built (only needed once)
            deploy {lib} (test|prod)  Upload to PyPi server

        Install:
            install sdist    {lib}  Install from local sdist
            install wheel    {lib}  Install from local wheel
            install pypitest {lib}  Install from PyPi test server
            install pypi     {lib}  Install from PyPi (official)

        Testing:
            test {lib}  Run unittests for the given lib in test env

        Help:
            -h | --help     display this message

    Libraries Available for Deployment: {lib}
        cqparts
        cqparts_bearings
        cqparts_fasteners
        cqparts_gearboxes
        cqparts_gears
        cqparts_misc
        cqparts_motors
        cqparts_springs
        cqparts_template
        cqparts_torquelimiters
        cqparts_toys

    Environments: {env}
        ubuntu-occ


## Host OS Setup

## Docker Images

Deployment testing is dependent on the docker containers built in `../env`

1. Build all base environments in the `../env/*` folders, then
1. Build each environment in the `env/*` folders

### Dependencies

Only needed when first setting up host machine...
or to update if it's been a while

```bash
./deploy.sh setup
```

### PyPi rc

`cat ~/.pypirc`

    [distutils]
    index-servers =
      prod
      test

    [prod]
    repository = https://upload.pypi.org/legacy/
    username=FraggaMuffin
    password=secret

    [test]
    repository=https://test.pypi.org/legacy/
    username=FraggaMuffin
    password=secret

`chmod 600 ~/.pypirc`


## Build and Test `sdist` and `wheel`

```bash
# specify the library you wish to deploy
#   (anything in the ../src folder)
lib=cqparts
```

**Build**

```bash
./deploy.sh build $lib
```

**Test `sdist`**

```bash
# per test envionrment
./deploy.sh env new ubuntu-occ
./deploy.sh env prereq $lib
./deploy.sh install sdist $lib
./deploy.sh env testreq
./deploy.sh test $lib
```

**Test `wheel`**

```bash
# per test envionrment
./deploy.sh env new ubuntu-occ
./deploy.sh install wheel $lib
./deploy.sh env testreq
./deploy.sh test $lib
```


## Upload to PyPi Test server

```bash
./deploy.sh deploy $lib test

# open published pypi page
xdg-open https://testpypi.python.org/pypi/$lib
# make sure it's sane
```

**Test**

```bash
# per test envionrment
./deploy.sh env new ubuntu-occ
./deploy.sh install pypitest $lib
./deploy.sh env testreq
./deploy.sh test $lib
```

## Upload to PyPy server

all good!? sweet :+1: time to upload to 'production'

```bash
./deploy.sh deploy $lib prod

# open published pypi page
xdg-open https://pypi.python.org/pypi/$lib
# make sure it's sane
```

**Test**

```bash
# per test envionrment
./deploy.sh env new ubuntu-occ
./deploy.sh install pypi $lib
./deploy.sh env testreq
./deploy.sh test $lib
```


# Deployment in Git

```
TODO: document git release process
```

the plan is to draw from `pygcode` again:

https://github.com/fragmuffin/pygcode/tree/master/deployment#deployment-in-git


# Announcements

Announce new releases as

## GitHub Issue

Raise an issue with "hey, new software!, yay"

```
TODO: add template text here
```

## Google Group Announcement

Publish message in `cadquery` google group:
https://groups.google.com/forum/#!forum/cadquery

```
TODO: add template text here
```
