import datetime
import logging
import os
import pathlib
import uuid

import papermill as exe
from loguru import logger
from notebooktoall.transform import write_files, get_notebook

from src.config import Constants
from src.model.jupyer_request import ExecutionStatus, Execution
from src.model.message import Status
from src.storage.cache_store import JupyterStore, JupyterExecutionStore

store = JupyterStore()
execution_store = JupyterExecutionStore()


async def get_status(name) -> ExecutionStatus:
    return execution_store.get(name)


async def store_file(name, file=None, dependencies=None) -> bool:
    if not file and not dependencies:
        return False
    if file:
        await store_notebook(file, name)
    if dependencies:
        await save_dependencies(name, dependencies)
    return True


async def store_notebook(file, name):
    os.makedirs(os.path.join(Constants.NOTEBOOK_STORE, name), exist_ok=True)
    nb_location = os.path.join(Constants.NOTEBOOK_STORE, name, file.filename)
    await __store(file, nb_location)
    store.put(name, nb_location)


async def save_dependencies(name, dependencies):
    for dependency in dependencies:
        await __store(dependency, os.path.join(Constants.NOTEBOOK_STORE, name, dependency.filename))


async def __store(file, save_name):
    with open(save_name, "wb+") as file_object:
        file_object.write(file.file.read())


async def output_notebook(name):
    input_path = pathlib.Path(store.get(name))
    default_data = f"""
    <html>
        <head>
            <title>{name} execution status</title>
        </head>
        <body>
            <p> No data available <p>
        </body>
    </html>
    """
    if not input_path:
        return default_data
    output_dir = os.path.join(input_path.parent, "outputs")
    output_html = pathlib.Path(os.path.join(output_dir, f"{input_path.stem}-output.html"))
    if not output_html or not output_html.exists():
        return default_data
    return output_html.read_text()


async def output(name, index=None):
    input_path = pathlib.Path(store.get(name))
    default_data = {"info": "No data available"}
    if not input_path:
        return default_data
    output_dir = os.path.join(input_path.parent, "outputs")
    output_text = pathlib.Path(os.path.join(output_dir, f"{input_path.stem}-stdout"))
    if not output_text or not output_text.exists():
        return default_data
    data = output_text.read_text().split("\n")
    return {"data": [data[index]]} if index and data else {"data": data or []}


def run(name, params={}, output_path=None):
    params = params or {}
    input_path = pathlib.Path(store.get(name))
    exe_id = uuid.uuid4().hex[:6].upper()
    update_execution_status(exe_id=exe_id, name=name, status=Status.STARTED, params=params)
    if not input_path.exists():
        return []
    stdout_file = None
    if output_path is None:
        notebook_name = input_path.stem
        suffix = input_path.suffix
        output_dir = os.path.join(input_path.parent, "outputs")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{notebook_name}-output{suffix}")
        stdout_file = open(os.path.join(output_dir, f"{notebook_name}-stdout"), "a+")
        update_execution_status(exe_id=exe_id, name=name, status=Status.RUNNING)
    try:
        rs = execute_jupyter(name, input_path, output_path, params, stdout_file)
        stdout_file.close()
        output = os.path.join(output_dir, f"{notebook_name}-output")
        logging.info(f"Execution of {name} completed")
        write_files(export_list=["html"], nb_node=get_notebook(output_path), file_name=output)
        logging.info(f"HTML generation of {name} completed")
        update_execution_status(exe_id=exe_id, name=name, status=Status.SUCCESS)
        return rs, output
    except Exception as e:
        logger.error("Error while running notebook:{}, with exception:{}", input_path, e)
        update_execution_status(exe_id=exe_id, name=name, status=Status.FAILURE, errors=[str(e)])
    return False


def execute_jupyter(name, input_path, output_path, params, stdout_file):
    return exe.execute_notebook(
        input_path,
        output_path,
        stdout_file=stdout_file,
        parameters={"id": name, **params}
    )


def update_execution_status(exe_id, name, status, params=None, errors=None):
    exe_status = execution_store.get(name, ExecutionStatus(name=name))
    if not exe_status.executions:
        exe_status.executions = {}
    execution = exe_status.executions.get(exe_id, Execution(exe_id=exe_id, parameters=params))
    execution.status = status
    exe_status.latest_status = status
    exe_status.latest_execution = exe_id
    if errors:
        errors_list = execution.errors or []
        errors_list.extend(errors)
        execution.errors = errors_list
    if status == Status.STARTED:
        execution.started_at = datetime.datetime.now()
    elif status == Status.FAILURE or status == Status.SUCCESS:
        execution.completed_by = datetime.datetime.now()
    exe_status.executions[exe_id] = execution
    execution_store.put(name, exe_status)
