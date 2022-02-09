#!/bin/bash
# Script for building LengthParser Agent and pushing to ECR repo

# TODO - local vars needed:
VERSION=''


# Local envars
APP_PATH=/tmp/build/LengthParser/$(date +%s)
AGENTS=$WORKING/Agents/ParserAgent
DATACONN=$WORKING/flask/app/DataConnect
source $AGENTS/build/helpers.sh

# Create build dir and copy source files
mkdir -p $APP_PATH
cd $APP_PATH
cp $DATACONN/Database.py $APP_PATH/
cp $DATACONN/Logger.py $APP_PATH/
cp $AGENTS/LengthParser.py $APP_PATH/
cp $AGENTS/Abstract.py $APP_PATH/
cp $AGENTS/build/length-parser.Dockerfile $APP_PATH/Dockerfile
cp $AGENTS/build/length-parser.requirements.txt $APP_PATH/requirements.txt

# Initialize build env and build image
export $(xargs < $DATACON/.secrets)
virtualenv $APP_PATH/venv
source $APP_PATH/venv/bin/activate
pip3 install -r requirements.txt
docker build . --tag "LengthParserAgent:$VERSION"
deactivate

# Tag image and push to AWS ECR
image_id=`imageID "LengthParserAgent:$VERSION"`
ecr_tag="$ECR_AGENTS_REPO_URI:LengthParserAgent$VERSION"
docker tag -t $image_id $ecr_tag
docker push $ecr_tag

