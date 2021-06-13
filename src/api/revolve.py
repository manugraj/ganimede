from fastapi import APIRouter
from fastapi.responses import Response
from fastapi import status

from src.model.jupyer_request import NotebookUpdate, NotebookBasic
from src.model.space import SpaceManagedResponse, UpdateFromSpaceResponse
from src.space import space_manager
from src.utils.crypto_utils import CrypticTalk

router = APIRouter(prefix="/api/v1/notebooks")


@router.post(
    "/edit", tags=["Jupyter Notebook Editor"],
    summary="Edit & test Jupyter Notebook",
    response_model=SpaceManagedResponse
)
async def edit_nb(name: str, version: int, token: str):
    return await space_manager.new_request(NotebookBasic(name=name, version=version), token, view=False)


@router.get(
    "/view", tags=["Jupyter Notebook Editor"],
    summary="View & test Jupyter Notebook",
    response_model=SpaceManagedResponse
)
async def view_nb(name: str, version: int, token: str):
    return await space_manager.new_request(NotebookBasic(name=name, version=version), token, view=True)


@router.post(
    "/update", tags=["Jupyter Updater"],
    summary="Update Jupyter Notebook with new version",
    response_model=UpdateFromSpaceResponse
)
async def update_nb(update_req: NotebookUpdate, token: str):
    return await space_manager.update(update_req, token)


@router.get(
    "/token", tags=["Utility"],
    summary="Get sample token",
    response_model={}
)
async def test_token(text: str, i_am: str, response: Response):
    if i_am == "vengeful_buddha":
        return {"token": CrypticTalk.def_encrypt(text), "warn": "DONOT use the API in production; follow standard "
                                                                "practices"}
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"error": "You are not one of us"}
