import uuid
from typing import List, Optional

from fastapi import APIRouter, UploadFile, File
from fastapi import BackgroundTasks
from fastapi.requests import Request
from fastapi.responses import HTMLResponse

from src.core import jupyter
from src.model import message
from src.model.jupyer_request import ExecutionStatus, Notebook, NotebookExecutionRequest, NotebookBasic

router = APIRouter(prefix="/api/v1/notebooks")


@router.post(
    "/define", tags=["Jupyter Notebook"],
    summary="Add Jupyter execution system",
    response_model=message.Response
)
async def add_definition(notebook: Notebook,
                         request: Request
                         ):
    return message.response(request=request, status=await jupyter.define(notebook))


@router.get(
    "/projects", tags=["Jupyter Notebook"],
    summary="See versions of all projects",
    response_model=message.Response
)
async def get_project_data(name: str, request: Request):
    data = await jupyter.get_project(name)
    return message.response(request=request, data=data, status=data is not None)


@router.post(
    "/store", tags=["Jupyter Notebook"],
    summary="Add Jupyter Notebook and associated files to system",
    response_model=message.Response
)
async def upload_notebook(name: str,
                          version: int,
                          request: Request,
                          notebook: UploadFile = File(None),
                          additional_files: Optional[List[UploadFile]] = File(None)):
    if notebook.filename and not notebook.filename.endswith("ipynb"):
        return message.response(request=request, status=False, info="Only Jupyter notebooks are allowed")
    return message.response(request=request, status=await jupyter.store_file(NotebookBasic(name=name, version=version),
                                                                             notebook,
                                                                             additional_files))


@router.post(
    "/run", tags=["Jupyter Notebook"],
    summary="Run Jupyter Notebook",
    response_model=message.Response
)
def run(exe_request: NotebookExecutionRequest, request: Request, tasks: BackgroundTasks):
    exe_request.exe_id = exe_request.exe_id or uuid.uuid4().hex[:6].upper()
    tasks.add_task(jupyter.run, exe_request)
    return message.response(request=request, status=True,
                            info=f"Execution started successfully with id: {exe_request.exe_id}")


@router.get(
    "/status", tags=["Jupyter Notebook"],
    summary="Get execution status",
    response_model=ExecutionStatus
)
async def status(name: str, version: int = 1):
    return await jupyter.get_status(NotebookBasic(name=name, version=version))


@router.get(
    "/html", tags=["Jupyter Notebook"],
    summary="Get output of execution",
    response_class=HTMLResponse
)
async def output(name: str, version: int = 1, execution_id: str = None):
    return await jupyter.output_html(NotebookBasic(name=name, version=version), execution_id)


@router.get(
    "/output", tags=["Jupyter Notebook"],
    summary="Get output of execution",
    response_model={}
)
async def output(name: str, version: int = 1, execution_id: str = None, cell: int = 0):
    return await jupyter.output_cell(NotebookBasic(name=name, version=version), execution_id, cell)


@router.get(
    "/plain_text", tags=["Jupyter Notebook"],
    summary="Get output of execution",
    response_model={}
)
async def output(name: str, version: int = 1, execution_id: str = None, index: int = 0):
    return await jupyter.output(NotebookBasic(name=name, version=version), execution_id, index)
