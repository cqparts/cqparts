FROM cqparts-env:ubuntu-py3

# build-time arguments
ARG tester_name=tester
ARG freecad_conda_ver=0.17-py36_11
ARG env_rel_path

ADD . /code
# FIXME: /code is added, so setup.sh may be run, but it's later replaced with a
#        volume mount in run.sh.
#        The "added" /code is not removed from the image... it's just messy
WORKDIR /code/tests
USER root
RUN bash /code/${env_rel_path}/setup.sh

# test user
USER ${tester_name}

# runtime environment variables
ENV FREECAD_LIB /opt/miniconda/pkgs/freecad-${freecad_conda_ver}/lib
ENV LD_LIBRARY_PATH /opt/miniconda/lib
ENV PYTHONPATH /code/${env_rel_path}/../python-lib

# default run command
CMD $PYTHON_BIN runtests.py --ignore "catalogue"
