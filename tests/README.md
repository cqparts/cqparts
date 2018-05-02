# Test Suite

Testing can be done in 2 ways, either:

- on your host's environment, or
- inside a `docker` container

Methods for setting up, and executing the test suite are documented below.

note: Both methods have only been tested on a Linux OS

## Host OS : `run.sh`

**Setup**

To install unittest requiremnets, you'll need the python packages listed in
`requirements.txt`. Install them with:

    pip install -r requirements.txt


**Executing**

Then you should be able to execute the tests with:

    ./run.sh

That will run a select collection of tests that test fundamental features of
`cqparts`.  The full test-suite includes catalogue tests that can take some time
to execute, but don't add a lot of value to quality confidence.

For more specific options you can run

    ./run.sh help

But for even more options, try:

    python runtests.py --help

## Docker Containers

The `env` folder contains docker environments to perform tests with tight
control on the environment their running in.

This is most useful in testing python 2/3 code compatability.

Read more in [the `env` folder](env)
