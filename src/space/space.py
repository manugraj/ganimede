import pathlib
import shutil
from string import Template

from src.config import Constants, SystemConfig
from src.core.jupyter import paths_store
from src.model.jupyer_request import NotebookBasic
from src.space.docker_file import docker_view_yaml, \
    docker_yaml, \
    docker_build_with_requirements, \
    docker_build_without_requirements
from src.storage.cache_store import NotebookData
from src.utils import system
from src.utils.crypto_utils import CrypticTalk
from src.utils.path_utils import paths, paths_and_create, paths_create
from src.utils.py_utils import pkg_info

nb_store = NotebookData()

def verify_integrity():
    return system.run("docker -v").return_code == 0 and system.run("docker-compose -v").return_code == 0


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


def paths_container(request_id, notebook: NotebookBasic):
    return paths(Constants.CONTAINER_DEFAULT, request_id, notebook.name,
                 str(notebook.version))


def paths_container_nb(request_id, notebook: NotebookBasic):
    return paths(Constants.CONTAINER_NB_DEFAULT, request_id, notebook.name,
                 str(notebook.version))


def prepare_env(notebook: NotebookBasic, token: str, request_id: str, view=True):
    port = system.free_port()
    container_path = paths_container(request_id, notebook)
    paths_create(container_path)
    container_nb_path = paths_container_nb(request_id, notebook)
    paths_create(container_nb_path)
    notebook_dir = paths_store(notebook.name, notebook.version)
    has_requirements = _generate_requirements(notebook, container_path)
    docker_file_name = _write_docker_file(container_path, has_requirements, notebook)
    _write_dc_yaml(container_path, container_nb_path, docker_file_name, notebook, token, request_id, port, view)
    _copy_contents(container_nb_path, notebook_dir)
    return pathlib.Path(container_path).absolute(), port, pathlib.Path(container_nb_path).absolute()


def _write_dc_yaml(container_path, container_nb_path, docker_file_name, notebook, token, request_id, port,
                   view_only=False):
    if view_only:
        yml = Template(docker_view_yaml).substitute(
            project_name=f"{notebook.fqn()}-r{request_id}".lower(),
            project_defn=docker_file_name,
            project_token=CrypticTalk.def_decrypt(token),
            project_path=pathlib.Path(container_nb_path).absolute(),
            port=port)
    else:
        yml = Template(docker_yaml).substitute(
            project_name=f"{notebook.fqn()}-r{request_id}".lower(),
            project_defn=docker_file_name,
            project_token=CrypticTalk.def_decrypt(token),
            project_path=pathlib.Path(container_nb_path).absolute(),
            port=port,
            nb_gid=system.run("id -g").out,
            nb_uid=system.run("id -u").out)
    write_file(container_path, "docker-compose.yml", yml)


def _write_docker_file(container_path, has_requirements, notebook):
    d_file = f'{notebook.fqn()}.dfile'
    write_file(container_path, d_file,
               docker_build_with_requirements if has_requirements else docker_build_without_requirements)
    return d_file
