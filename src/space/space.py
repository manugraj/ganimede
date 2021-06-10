import pathlib
import shutil
from string import Template

import delegator
import portpicker

from src.config import Constants
from src.model.jupyer_request import NotebookBasic
from src.storage.cache_store import NotebookData
from src.utils.crypto_utils import to_hash_argon2, CrypticTalk
from src.utils.path_utils import paths, paths_and_create
from src.utils.py_utils import pkg_info

_docker_build_with_requirements = '''
ARG BASE_CONTAINER=docker.io/jupyter/minimal-notebook:latest
FROM $BASE_CONTAINER
COPY requirements.txt requirements.txt
RUN mkdir -p data
RUN python3 -m pip install -r requirements.txt
'''

_docker_build_without_requirements = '''
ARG BASE_CONTAINER=docker.io/jupyter/minimal-notebook:latest
FROM $BASE_CONTAINER
RUN mkdir -p data
'''

_docker_yaml = '''
version: "3"
services:
  jupyter:
    container_name: $project_name
    build:
      context: ./
      dockerfile: $project_defn
    environment:
      - JUPYTER_ENABLE_LAB=yes
      - JUPYTER_TOKEN=$project_token
    volumes:
    - $project_path:/home/jovyan/work
    ports:
        - $port:8888
'''

nb_store = NotebookData()


def verify():
    return delegator.run("podman -v").return_code == 0


def _generate_requirements(notebook: NotebookBasic, container_path):
    requirements = []
    requirements_data = nb_store.get_data(notebook.name, notebook.version)
    for key in requirements_data:
        requirements.append(pkg_info(key, requirements_data.get(key, "")))
    if requirements:
        write_file(container_path, "requirements.txt", '\n'.join(requirements))
        return True
    return False


def write_file(container_path, file, requirements):
    pathlib.Path(paths(container_path, file)).write_text(requirements, encoding='utf-8')


def _copy_contents(container_path, notebook_dir):
    shutil.copytree(notebook_dir, container_path, dirs_exist_ok=True)


def prepare_env(notebook: NotebookBasic, token: str, request_id: str):
    port = portpicker.pick_unused_port()
    container_path = paths_and_create(Constants.CONTAINER_DEFAULT, request_id, notebook.name, str(notebook.version))
    container_nb_path = paths_and_create(Constants.CONTAINER_DEFAULT, Constants.CONTAINER_NB_DEFAULT, request_id,
                                         notebook.name, str(notebook.version))
    notebook_dir = paths(Constants.NOTEBOOK_STORE, notebook.name, str(notebook.version))
    has_requirements = _generate_requirements(notebook, container_path)
    docker_file_name = _write_docker_file(container_path, has_requirements, notebook)
    _write_dc_yaml(container_path, container_nb_path, docker_file_name, notebook, token, request_id, port)
    _copy_contents(container_nb_path, notebook_dir)
    return pathlib.Path(container_path).absolute(), port


def _write_dc_yaml(container_path, container_nb_path, docker_file_name, notebook, token, request_id, port):
    write_file(container_path, "docker-compose.yml", Template(_docker_yaml)
               .substitute(project_name=f"{notebook.fqn()}-r{request_id}",
                           project_defn=docker_file_name,
                           project_token=CrypticTalk.def_decrypt(token),
                           project_path=pathlib.Path(
                               container_nb_path).absolute(),
                           port=port))


def _write_docker_file(container_path, has_requirements, notebook):
    d_file = f'{notebook.fqn()}.dfile'
    write_file(container_path, d_file,
               _docker_build_with_requirements if has_requirements else _docker_build_without_requirements)
    return d_file
