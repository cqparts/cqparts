FROM ubuntu:16.04

# build-time arguments
ARG tester_name=tester
ARG freecad_conda_ver=0.17-py36_11
ARG env_rel_path

ADD . /code
# FIXME: /code is added, so setup.sh may be run, but it's later replaced with a
#        volume mount in run.sh.
#        The "added" /code is not removed from the image... it's just messy
WORKDIR /code
RUN bash /code/${env_rel_path}/setup.sh

# test user
RUN useradd -c 'test user' -m -d /home/${tester_name} -s /bin/bash ${tester_name}
#RUN chown -R ${tester_name}.${tester_name} /code
USER ${tester_name}
ENV HOME /home/${tester_name}

# default run command
CMD echo "image command run successfully... but it does nothing"
