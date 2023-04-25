# Neuro NER Docker creator

This repository contains a Python application that creates a Flask server to serve a NeuroNER API. NeuroNER is a named entity recognition (NER) system that uses deep learning to identify entities in text. With this API, you can easily integrate NeuroNER into your applications.

# Files

In the root folder create a folder named model and in here store your Neuro NER pickle and checkpoint files.
the root directory should look like this.

> model
>
> > - parameters.ini
> > - dataset.pickle
> > - model.ckpt.data-0000-of-000001
> > - model.ckpt.index
> > - model.ckpt.meta
>
> PharmaCoNER-Tagger
> Dockerfile
> app.py

---

## Create Docker image

    docker build -t <name_of_image> .

## Run image

    docker run  -p 8003:5000 -t <name_of_image>

## Tag image to upload to github

    docker tag <name_of_image>:latest <github_user>/<name_of_image>

## Push to docker

    docker push <github_user>/<name_of_image>:latest
