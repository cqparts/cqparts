FROM cqparts-env:ubuntu-py3

# build-time arguments
ARG tester_name=tester
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
ENV PYTHONPATH /code/src:/code/${env_rel_path}/../python-lib

# default run command
CMD bash run.sh
