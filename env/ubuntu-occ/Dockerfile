FROM ubuntu:16.04

# build-time arguments
ARG tester_name=tester
ARG freecad_conda_ver_major=0.18b0
ARG freecad_conda_ver_minor=py36h275e31e_2
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

# runtime environment variables
ENV PIP_BIN pip3
ENV PYTHON_BIN python3
ENV LD_LIBRARY_PATH /opt/miniconda/lib
# freecad version folder: delimited with '-'
ENV FREECAD_LIB /opt/miniconda/pkgs/freecad-${freecad_conda_ver_major}-${freecad_conda_ver_minor}/lib

# default run command
CMD echo "image command run successfully... but it does nothing"
