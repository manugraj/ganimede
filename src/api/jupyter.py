from typing import List, Optional

from fastapi import APIRouter, UploadFile, File
from fastapi.requests import Request
from fastapi import BackgroundTasks

from src.core import jupyter
from src.model import message
from src.model.jupyer_request import Parameters, ExecutionStatus
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/api/v1/notebooks")


@router.post(
    "/store", tags=["Jupyter Notebook"],
    summary="Add Jupyter Notebook and associated files to system",
    response_model=message.Response
)
async def upload_notebook(name: str,
                          request: Request,
                          notebook: UploadFile = File(None),
                          additional_files: Optional[List[UploadFile]] = File(None)):
    if notebook.filename and not notebook.filename.endswith("ipynb"):
        return message.response(request=request, status=False, info="Only Jupyter notebooks are allowed")
    return message.response(request=request, status=await jupyter.store_file(name, notebook, additional_files))


@router.post(
    "/run", tags=["Jupyter Notebook"],
    summary="Run Jupyter Notebook",
    response_model=message.Response
)
def run(name: str, parameters: Parameters, request: Request, tasks: BackgroundTasks):
    tasks.add_task(jupyter.run, name, parameters.data)
    return message.response(request=request, status=True, info="Execution started")


@router.get(
    "/status", tags=["Jupyter Notebook"],
    summary="Get execution status",
    response_model=ExecutionStatus
)
async def status(name: str):
    return await jupyter.get_status(name)


@router.get(
    "/notebook", tags=["Jupyter Notebook"],
    summary="Get output of execution",
    response_class=HTMLResponse
)
async def output(name: str):
    return await jupyter.output_notebook(name)


@router.get(
    "/output", tags=["Jupyter Notebook"],
    summary="Get output of execution",
    response_model={}
)
async def output(name: str, index: int = None):
    return await jupyter.output(name, index)
