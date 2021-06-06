#!/bin/bash

APP_PATH=/home/user/Documents/humansdetected

virtualenv $APP_PATH/app/Agent/venv
source $APP_PATH/app/Agent/venv/bin/activate
pip3 install -r $APP_PATH/app/Agent/requirements.txt
docker build --tag 'humans-agent:1.0' $APP_PATH/app/Agent
deactivate


