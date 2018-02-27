FROM ubuntu:16.04

# build-time arguments
ARG tester_name=tester
ARG env_rel_path

ADD . /code
WORKDIR /code/tests
RUN bash /code/${env_rel_path}/setup.sh

# test user
RUN useradd -c 'test user' -m -d /home/${tester_name} -s /bin/bash ${tester_name}
#RUN chown -R ${tester_name}.${tester_name} /code
USER ${tester_name}
ENV HOME /home/${tester_name}

# runtime
CMD ["python2", "runtests.py", "--ignore", "catalogue"]
