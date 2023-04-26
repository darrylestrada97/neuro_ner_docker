#!/bin/bash

#important!!!! Before runing this script you have to log in to your docker hub user
# for this, run docker login and follow the step. Then run the script.


DOCKER_USERNAME=bsctemu
# Define the directories
# SOURCE_DIR is the directory where all the models are, inside this folder
# there should be a folder per model, the name os the folder will be used to 
# create the image name. 
SOURCE_DIR=~/models
#MODELS_DIR is where the neuro_ner_docker/model/ folder is, in this case in in my home directory
# so I only added ~/ to it.
MODELS_DIR=~/neuro_ner_docker/model/



# Move the contents of each folder to MODELS_DIR
for folder in $SOURCE_DIR/*; do
  if [ -d "$folder" ]; then
    folder_name=$(basename $folder)
    rm "$MODELS_DIR/"*
    cp "$folder"/* "$MODELS_DIR/"
    # Build Docker image
    docker build -t $DOCKER_USERNAME/$folder_name .
    # Tag and push Docker image
    docker tag $DOCKER_USERNAME/$folder_name $DOCKER_USERNAME/$folder_name:latest
    docker push $DOCKER_USERNAME/$folder_name:latest
  fi
done


