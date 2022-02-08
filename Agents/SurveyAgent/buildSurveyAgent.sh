#!/bin/bash

APP_PATH=/home/user/repos/humansdetected/Agents

virtualenv $APP_PATH/SurveyAgent/venv
source $APP_PATH/SurveyAgent/venv/bin/activate
pip3 install -r $APP_PATH/SurveyAgent/requirements.txt
docker build --tag 'HumD-survey-agent:1.0' $APP_PATH/SurveyAgent
deactivate


