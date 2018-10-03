# Test Environments

Each of the sub-folders in this directory has a buildable environment designed
to for unit-testing.

**IMPORTANT:** Each of these environments is based on a docker image built in
the root `env` folder.
Before building these environments, run the relevant `build.sh` scripts in
[the root `env` folder](../../env)

At this time [2018-02] I'm just working with docker containers with _ubuntu_
environments.

## `python-lib`

This folder will be added to the environment's `PYTHONPATH`; any libs in this
folder will be referenced before those installed in the container.

Used to test parallel development with other libraries, mainly `cadquery`.

However, this folder should be empty when testing for a release; all dependent
libraries should be acquired from their public sources (eg: `pip`).

## `ubuntu-py2`

docker image hosting ubuntu with python 2.x to run tests.

```bash
cd ubuntu-py2
./build.sh
./run.sh
```

## `ubuntu-py3`

docker image hosting ubuntu with python 3.x to run tests.

```bash
cd ubuntu-py3
./build.sh
./run.sh
```

## Windows (?)

Ideally I'd also have a _windows_ testing environment as well, however I'm
just a little fuzzy on how to run a licensed windows box to a similar degree
of independence as the docker containers used to test _linux_ environments.

For example, do I need 2 windows licenses to test under python2 and python3...
there's no way I'm spending that money.
