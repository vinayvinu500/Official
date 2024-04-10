ECHO OFF

@REM ECHO running the docker container from an image
@REM docker run -it ubuntu /bin/bash

@REM ECHO Running the mutliple docker ubuntu containers for an image
@REM docker run -it -d --rm --name ubuntu1 ubuntu /bin/bash
@REM docker run -it -d --rm --name ubuntu2 ubuntu /bin/bash
@REM docker run -it -d --rm --name ubuntu3 ubuntu /bin/bash

@REM ECHO Extract a rar file
@REM docker run --rm -v "%CD%:/files" ubuntu bash -c "apt-get update && apt-get install -y unrar && unrar x -r /files/my_appraisal_contents.rar"

@REM ECHO Nodejs repl tool
@REM docker run -it --rm --name node node:7.7.4-alpine

@REM ECHO Python repl tool
@REM docker run -it --rm --name python3.11 python:3.11

ECHO MySQL repl tool
docker run -it --rm --name mysql mysql:latest --MYSQL_ROOT_PASSWORD Vinay@01
