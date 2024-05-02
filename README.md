# Docker WoL

Made for Python 3.12

## Dependencies

    - flet = GUI
    - pip-tools = Generate requirements.txt from .in

## Generate requirements.txt with pip-tool

pip-compile requirements.in

## Build docker image and run image from the docker container

docker build --tag emberlightvfx/wol:latest .
docker run -d --network host -p 8080:8080 emberlightvfx/wol
