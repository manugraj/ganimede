from fastapi import APIRouter

from src.model.jupyer_request import NotebookBasic
from src.model.message import Status
from src.space.space import prepare_env
from src.utils import docker_cli
from src.utils.crypto_utils import CrypticTalk
from src.utils.path_utils import paths

router = APIRouter(prefix="/api/v1/notebooks")


@router.post(
    "/test", tags=["Jupyter Notebook Editor"],
    summary="Edit & test Jupyter Notebook",
    response_model={}
)
async def edit_nb(name: str, version: int, request_id: str, token: str):
    path, port = prepare_env(NotebookBasic(name=name, version=version), CrypticTalk.def_encrypt(token), request_id)
    d_status = docker_cli.docker("-v")
    dc_status = docker_cli.docker_compose("-v")
    if d_status["status"] == dc_status["status"] == Status.SUCCESS.value:
        deployment = docker_cli.docker_compose(f"-f {paths(path, 'docker-compose.yml')} up -d")
        if deployment["status"] == Status.SUCCESS.value:
            return {"url": f"http://localhost:{port}"}
        else:
            return {"info": "Deployment failed. Please contact admin"}
    else:
        return {"info": "Required systems are not installed. Please contact admin"}


@router.get(
    "/token", tags=["Utility"],
    summary="Get sample token",
    response_model={}
)
async def token(text: str):
    return {"token": CrypticTalk.def_encrypt(text)}
