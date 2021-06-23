# Ganimede - Run Jupyter notebook via ReST API

<a href="https://www.producthunt.com/posts/ganimede?utm_source=badge-featured&utm_medium=badge&utm_souce=badge-ganimede" target="_blank"><img src="https://api.producthunt.com/widgets/embed-image/v1/featured.svg?post_id=299971&theme=dark" alt="Ganimede - Painless jupyter notebook management for data pipelines | Product Hunt" style="width: 250px; height: 54px;" width="250" height="54" /></a>

[![Mentioned in Awesome <awesome-jupyter>](https://awesome.re/mentioned-badge.svg)](https://github.com/markusschanta/awesome-jupyter)

An fastAPI based system to run Jupyter via ReST interface


## Use cases
- Ability to write machine learning logic and expose them to systems as rest api
- Write Jupyter nb locally and run them in a centralised powerful machine to reduce cost
- Create framework to directly connect Jupyter notebook to other systems 

## Requirements
- docker
- redis

## Stack
- Redis
- FastAPI
- Papermill
- Jupyter
- Poetry
- Docker

## Build
- Clone the repo
- Run `poetry install`
- Run `run.py` or `scripts\launch.sh` or `cd docker;docker-compose up -d`

## Deployment
- Clone the repo and in `docker` folder, run `docker-compose build`. The docker image will be build
- Push to registry or use your custom publishing method to publish the image

## API Docs
- Start the application
- Go to `localhost:8000/docs` for swagger and `localhost:8000/redoc` for redoc

### Main APIs

#### Jupyter Notebook
- `define` for defining projects and its dependencies
- `store` for storing notebook and associated files
- `run` for executing a jupyter file
- `html` to get a rendered page of executed notebook
- `output` to get the output of Jupyter execution in json format
- `plain_text` to get the plain text output

#### Jupyter Notebook Editor
- `edit` for editing notebook in a sandbox
- `view` for viewing notebook in sandbox and can run it, but not save the changes

#### Jupyter Updater
- `update` for storing the next version of notebook from `edit` endpoint

## TODO
- [x] Provide live environment for editing and running jupyter
- [ ] Custom transformations for jupyter output
- [ ] Scheduled cleanup of created jupyter docker containers
- [ ] Change container implementation to podman or other rootless systems
