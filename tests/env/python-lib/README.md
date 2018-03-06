# Python Libraries for Test

Any modules stored in this folder will be imported before anything installed
in the test environments.

## `cadquery` as an example

The parallel development of the `cadquery` library with `cqparts` has been
necessary for early stages of developing `cqparts`, this is how testing is done
with different sources of `cadquery`

### `cadquery` installed from `pip`

With no additions to the `python-lib` folder, we can run the following commands
to see that the default imported `cadquery` version has been installed in the
docker image.

Running a python console inside the `ubuntu-py2` environment, with `$CWD` as
this `python-lib` folder:

    $ cd ubuntu-py2
    $ ./run.sh python
    Python 2.7.12 (default, Dec  4 2017, 14:50:18)
    [GCC 5.4.0 20160609] on linux2
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import cadquery
    >>> cadquery
    <module 'cadquery' from '/usr/local/lib/python2.7/dist-packages/cadquery/__init__.pyc'>

### Custom `cadquery` branch

If we wish to use a specific branch from the `cadquery` (or in fact any
fork of that repository), we can add it to this `python-lib` folder

Adding the `cadquery` repository, let's put it into a sub-folder:

    $ mkdir _repos
    $ cd _repos

    # clone the repo into a "cadquery" folder, with "master" checked out
    $ git clone git@github.com:dcowden/cadquery.git

    $ cd .. # back to the python-lib folder

    # create a cadquery symlink to the module inside the repository
    $ ln -s _repos/cadquery/cadquery cadquery

Gives us the directory structure:

    .
    ├── cadquery -> _repos/cadquery/cadquery (the symlink we created)
    ├── README.md (this file)
    └── _repos
        └── cadquery ("master" branch, or whatever you decide to checkout)
            ├── ... truncated
            └── cadquery
                ├── ... truncated
                └── __init__.py

Now we can re-run the above commands (streamlined into one line) to show that
we're now picking up the `cadquery` library from our github repository clone:

    $ cd ubuntu-py2
    $ ./run.sh python -c 'import cadquery; print(cadquery)'
    <module 'cadquery' from '/code/tests/env/python-lib/cadquery/__init__.pyc'>
