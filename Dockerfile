FROM ubuntu:14.04
MAINTAINER Benson Wong <@mostlygeek>

ENV PYTHON_VER 2.6

ENV DEBIAN_FRONTEND noninteractive

# Install System Dependencies
RUN apt-get update &&  \
    apt-get -y install curl sqlite3 build-essential

# Install Pyrun environment into /app
RUN cd /tmp && \
    curl -qO https://downloads.egenix.com/python/install-pyrun && \
    bash install-pyrun --python=${PYTHON_VER} /app

# Install Token Server + requirements into /app
COPY . /app/
RUN cd /app && \
    ./bin/pip install -r requirements.txt && \
    ./bin/python ./setup.py develop

ENV DEBIAN_FRONTEND dialog
