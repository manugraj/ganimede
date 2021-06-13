from dataclasses import dataclass

from src.core import jupyter
from src.model.jupyer_request import NotebookBasic, DependencyLog, Notebook, NotebookUpdate
from src.model.message import Status
from src.model.space import SpaceManagedResponse, UpdateFromSpaceResponse
from src.space import space
from src.storage.cache_store import RequestStore, JupyterStore
from src.utils import docker_cli, system, crypto_utils
from src.utils.crypto_utils import CrypticTalk
from src.utils.path_utils import paths

request_store = RequestStore()
store = JupyterStore()


@dataclass
class SpaceRequest:
    request_id: str
    token: str


async def new_request(notebook: NotebookBasic, token: str, view=True) -> SpaceManagedResponse:
    try:
        request_id = crypto_utils.unique(6)
        path, port, nb_path = space.prepare_env(notebook, token, request_id, view)
        request_store.put(SpaceRequest(token=CrypticTalk.def_decrypt(token), request_id=request_id), nb_path)
        return await _create_new(path, port, request_id)
    except Exception as e:
        return SpaceManagedResponse(error=[f"Deployment failed due to exception:{str(e)}."])


async def update(update_req: NotebookUpdate, token: str) -> UpdateFromSpaceResponse:
    try:
        nb_loc = request_store.get(SpaceRequest(token=CrypticTalk.def_decrypt(token), request_id=update_req.request_id))
        if not nb_loc:
            return  UpdateFromSpaceResponse(request=update_req,
                                            status=Status.FAILURE,
                                            error=["No valid change set found"])
        if not jupyter.get_status(update_req.base_nb):
            return UpdateFromSpaceResponse(request=update_req,
                                           status=Status.FAILURE,
                                           error=["Invalid request"])
        log = DependencyLog()
        log.dependency_versions = [update_req.base_nb.version]
        book = Notebook(name=update_req.base_nb.name, version=update_req.new_version, dependency_log=log)
        defined_book = await jupyter.define(book)
        await jupyter.copy_notebook(notebook=book, from_location=nb_loc)
        info = "Version updated automatically" if not defined_book.version == update_req.new_version else None
        return UpdateFromSpaceResponse(request=defined_book, status=Status.SUCCESS,
                                       info=info)
    except Exception as e:
        return UpdateFromSpaceResponse(request=update_req, status=Status.FAILURE, error=[str(e)])


async def _create_new(path, port, request_id) -> SpaceManagedResponse:
    if space.verify_integrity():
        deployment = docker_cli.docker_compose(f"-f {paths(path, 'docker-compose.yml')} up -d")
        if deployment["status"] == Status.SUCCESS.value:
            return SpaceManagedResponse(url=f'http://{system.ip()}:{port}', request_id=request_id)
        else:
            return SpaceManagedResponse(error=["Deployment failed. Please contact admin"])
    else:
        return SpaceManagedResponse(error=["Required systems are not installed. Please contact admin"])
