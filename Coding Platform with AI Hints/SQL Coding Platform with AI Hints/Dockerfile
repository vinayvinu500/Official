FROM ubuntu:trusty
FROM python:3.11
FROM mysql:latest

RUN sudo apt-get -y update
RUN sudo apt-get -y upgrade 
RUN sudo apt-get install -y sqlite3 libsqlite3-dev
RUN mkdir /db
RUN /usr/bin/sqlite3 /db/test.db
CMD /bin/bash

# docker run -it -v /home/Sessions/:/db image_name 