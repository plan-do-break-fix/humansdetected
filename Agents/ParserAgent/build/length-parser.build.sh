#!/bin/bash
# Script for building LengthParser Agent and pushing to ECR repo

# Validate argument as version number 
VERSION=$1
re='^[0-9]+(\.[0-9]){0,2}$'
if ! [[$VERSION =~ $re]]
then
  echo "ParserAgent build scripts must be called with a valid container version."
  exit 1

# Local envars
echo "Initializing local variables"
APP_PATH=/tmp/build/LengthParser/$(date +%s)
AGENTS=$WORKING/Agents/ParserAgent
DATACONN=$WORKING/flask/app/DataConnect
source $AGENTS/build/helpers.sh

# Create build dir and copy source files
echo "Creating temporary build files"
mkdir -p $APP_PATH
cd $APP_PATH
cp $DATACONN/Database.py $APP_PATH/
cp $DATACONN/Logger.py $APP_PATH/
cp $AGENTS/LengthParser.py $APP_PATH/
cp $AGENTS/Abstract.py $APP_PATH/
cp $AGENTS/build/length-parser.Dockerfile $APP_PATH/Dockerfile
cp $AGENTS/build/length-parser.requirements.txt $APP_PATH/requirements.txt

# Initialize build env and build image
echo "Building image"
export $(xargs < $DATACON/.secrets)
virtualenv $APP_PATH/venv
source $APP_PATH/venv/bin/activate
pip3 install -r requirements.txt
docker build . --tag "LengthParserAgent:$VERSION"
deactivate

# Tag image and push to AWS ECR
echo "Pushing image $imageID to ECR repository"
image_id=`imageID "LengthParserAgent:$VERSION"`
ecr_tag="$ECR_AGENTS_REPO_URI:LengthParserAgent$VERSION"
docker tag -t $image_id $ecr_tag
docker push $ecr_tag

echo "Build completed. I hope the deployment goes well."
exit 0

