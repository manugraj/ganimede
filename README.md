# Ganimede - Run Jupyter notebook via ReST API

An fastAPI based system to run Jupyter via ReST interface


## Use cases
- Ability to write machine learning logic and expose them to systems as rest api
- Write Jupyter nb locally and run them in a centralised powerful machine to reduce cost
- Create framework to directly connect Jupyter notebook to other systems 


## Stack
- Redis
- FastAPI
- Papermill
- Jupyter
- Poetry

## Build
- Clone the repo
- Run `poetry install`
- Run `run.py` or `scripts\launch.sh` or `cd docker;docker-compose up -d`

## Deployment
- Clone the repo and in `docker` folder, run `docker-compose build`. The docker image will be build
- Push to registry or use your custom publishing method to publish the image

## TODO
- [ ] Provide live environment for editing and running jupyter
- [ ] Custom transformations for jupyter output