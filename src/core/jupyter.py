import datetime
import json
import pathlib
from collections import OrderedDict

import papermill as exe
from loguru import logger
from notebooktoall.transform import write_files, get_notebook
from virtualenvapi.manage import VirtualEnvironment

from src.config import Constants
from src.model.jupyer_request import ExecutionStatus, Execution, Notebook, NotebookBasic, NotebookExecutionRequest, \
    NotebookVersions
from src.model.message import Status
from src.storage.cache_store import JupyterStore, JupyterExecutionStore, NotebookData, EnvData
from src.utils import system
from src.utils.path_utils import paths, paths_create, search, store_file_at, store_text_at
from src.utils.py_utils import pkg_info

store = JupyterStore()
execution_store = JupyterExecutionStore()
nb_store = NotebookData()
env_store = EnvData()


def exception_handled(func):
    async def inner_function(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except IndexError:
            logger.error("IndexError caught by handler")
            return {"error": ["Invalid arguments"]}
        except Exception as e:
            logger.error("Exception caught by handler: {}", e)
            return {"error": [str(e)]}

    return inner_function


async def next_version(nb: NotebookBasic):
    if nb_store.exists(nb.name):
        return list(
            OrderedDict(sorted(nb_store.get_version(nb.name).items() or [0], key=lambda t: t[0])).keys() or [0]
        )[-1] + 1
    else:
        return 1


async def max_version(nb: NotebookBasic):
    if nb_store.exists(nb.name):
        return list(
            OrderedDict(sorted(nb_store.get_version(nb.name).items() or [0], key=lambda t: t[0])).keys() or [0]
        )[-1]
    else:
        return 0


async def get_project(name: str):
    return nb_store.get(name, NotebookVersions(name=name, versions={}))


async def get_status(notebook: NotebookBasic) -> ExecutionStatus:
    return execution_store.get(notebook.fqn())


async def store_file(notebook: NotebookBasic, file=None, associated_files=None) -> bool:
    nb_location = paths_store(notebook.name, notebook.version)
    paths_create(nb_location)
    if not file and not associated_files:
        return False
    if file:
        await _store_notebook(notebook, file, nb_location)
    if associated_files:
        await _save_associated_files(notebook, associated_files, nb_location)
    return True


async def copy_notebook(notebook: NotebookBasic, from_location) -> bool:
    nb_location = paths_store(notebook.name, notebook.version)
    paths_create(nb_location)
    path_fqn, files = search(from_location, "ipynb")
    if files:
        notebook_file = files[0]
        with open(paths(path_fqn, notebook_file), 'r') as f:
            new_file = f.read()
        return await _store_notebook_text(notebook=notebook, text=new_file, file_name=notebook_file,
                                          location=nb_location)
    return False


async def define(notebook: Notebook) -> bool:
    if notebook.version <= await max_version(notebook):
        notebook.version = await next_version(notebook)
    nb_store.add_version(notebook.name, notebook.version, await _prepare_dependency_matrix(notebook))
    env_store.rm(notebook.fqn())
    return notebook


async def _prepare_dependency_matrix(notebook: Notebook):
    requirements = {}
    if notebook.dependency_log:
        requirements: dict = notebook.dependency_log.requirements or {}
        dependent_versions = notebook.dependency_log.dependency_versions or {}
        for d_version in dependent_versions:
            versions_data: dict = nb_store.get_data(notebook.name, d_version)
            requirements.update(versions_data)
    return requirements


def _prepare_env(notebook: Notebook, requirements: dict = None):
    kernel = _kernel_name(notebook)
    paths_env = _paths_env(kernel)
    paths_create(paths_env)
    env = VirtualEnvironment(paths_env)
    if requirements:
        for pkg, version in requirements.items():
            ipkg = pkg_info(pkg, version)
            env.install(ipkg)
            logger.debug(f"Installing {ipkg} in {kernel}")
    env.install("jupyter")
    env.install("ipykernel")
    cmd = system.cmd(f'{paths(env.path, "bin", "ipython")} kernel install --name {kernel} --user')
    return cmd.return_code == 0


def _kernel_name(notebook: NotebookBasic):
    return notebook.fqn()


async def _store_notebook(notebook, file, location):
    save_name = paths(location, file.filename)
    await store_file_at(file, save_name)
    store.put(notebook.fqn(), save_name)


async def _store_notebook_text(notebook, text, file_name, location):
    save_name = paths(location, file_name)
    await store_text_at(text, save_name)
    store.put(notebook.fqn(), save_name)
    return True


async def _save_associated_files(other_files, location):
    for file in other_files:
        await store(file, paths(location, file.filename))


async def output_html(notebook: NotebookBasic, execution_id: str):
    default_data = f'''
    <html>
        <head>
            <title>{notebook.fqn()}-iteration.{execution_id} execution status</title>
        </head>
        <body>
            <p> No data available <p>
        </body>
    </html>
    '''
    if not execution_id:
        status: ExecutionStatus = await get_status(notebook)
        if status:
            execution_id = status.latest_execution
        else:
            return default_data
    output_dir, output_file, stdout_file, output_file_name = _mk_output_paths(notebook, execution_id, make=False)
    output_html_data = pathlib.Path(f"{output_file_name}.html")
    if not output_html_data or not output_html_data.exists():
        return default_data
    return output_html_data.read_text()


@exception_handled
async def output(notebook: NotebookBasic, execution_id: str = None, index=None):
    if not execution_id:
        status: ExecutionStatus = await get_status(notebook)
        if status:
            execution_id = status.latest_execution
        else:
            return {"data": ["No data available"]}
    output_dir, output_file, stdout_file, output_file_name = _mk_output_paths(notebook, execution_id, make=False)
    output_text = pathlib.Path(stdout_file)
    if not output_text or not output_text.exists():
        return {"data": []}
    data = output_text.read_text().split("\n")
    return {"data": [data[index]]} if index and data else {"data": data or []}


@exception_handled
async def output_cell(notebook: NotebookBasic, execution_id: str = None, cell=None):
    if not execution_id:
        status: ExecutionStatus = await get_status(notebook)
        if status:
            execution_id = status.latest_execution
        else:
            return {"info": "No data available"}
    output_dir, output_file, stdout_file, output_file_name = _mk_output_paths(notebook, execution_id, make=False)
    output_text = pathlib.Path(output_file)
    if not output_text or not output_text.exists():
        return {"info": "No data available"}
    data = json.loads(output_text.read_text())
    return {"data": data['cells'][cell]['outputs']} if cell and data else {"data": data or []}


def run(notebook: NotebookExecutionRequest):
    params = notebook.parameters or {}
    fqn = notebook.fqn()
    if not env_store.get(notebook.fqn(), False):
        env_store.put(notebook.fqn(), _prepare_env(notebook, nb_store.get_data(notebook.name, notebook.version)))

    notebook_exe_id = notebook.exe_id

    _update_execution_status(exe_id=notebook_exe_id, name=fqn, status=Status.STARTED, params=params)

    if not store.exists(fqn):
        _update_execution_status(exe_id=notebook_exe_id,
                                 name=fqn,
                                 status=Status.FAILURE,
                                 params=params,
                                 errors=["No notebook stored"])
        logger.error(f"No notebook stored for {notebook.fqn()}")
        return False

    notebook_file = pathlib.Path(store.get(fqn))

    if not notebook_file.exists():
        _update_execution_status(exe_id=notebook_exe_id,
                                 name=fqn,
                                 status=Status.FAILURE,
                                 params=params,
                                 errors=["Corrupted notebook data"])
        logger.error(f"Corrupted notebook data for {notebook.fqn()}")
        return False

    output_dir, output_file, stdout_file_name, output_file_name = _mk_output_paths(notebook, notebook_exe_id, make=True)

    _update_execution_status(exe_id=notebook_exe_id, name=fqn, status=Status.RUNNING)
    try:
        stdout_file = open(stdout_file_name, "a+")
        _execute_jupyter(notebook, notebook_file, output_file, params, stdout_file)

        stdout_file.close()
        logger.info(f"Execution of {fqn} completed")

        write_files(export_list=["html"], nb_node=get_notebook(output_file), file_name=output_file_name)
        logger.info(f"HTML generation of {fqn} completed")

        _update_execution_status(exe_id=notebook_exe_id, name=fqn, status=Status.SUCCESS)
        return True
    except Exception as e:
        logger.error("Error while running notebook:{}, with exception:{}", notebook_file, e)
        _update_execution_status(exe_id=notebook_exe_id, name=fqn, status=Status.FAILURE, errors=[str(e)])
        return False


def _mk_output_paths(notebook, notebook_exe_id, make=False):
    output_dir = paths_out(notebook.name, notebook.version, notebook_exe_id)
    if make:
        paths_create(output_dir)
    output_file = paths(output_dir, Constants.DEFAULT_OUT_FILE)
    stdout_file = paths(output_dir, Constants.DEFAULT_STDOUT_FILE)
    output_file_name = paths(output_dir, Constants.DEFAULT_OUT_FILE_NAME)
    return output_dir, output_file, stdout_file, output_file_name


def paths_store(project_name, project_version):
    return paths(Constants.NOTEBOOK_STORE,
                 project_name,
                 str(project_version))


def _paths_env(name):
    return paths(Constants.ENVIRONMENTS, name)


def paths_out(project_name, project_version, iteration_name):
    return paths(Constants.NOTEBOOK_OUTPUT,
                 project_name,
                 str(project_version),
                 iteration_name)


def _execute_jupyter(notebook, input_path, output_path, params, stdout_file):
    return exe.execute_notebook(
        input_path,
        output_path,
        stdout_file=stdout_file,
        parameters={"id": notebook.fqn(), **params},
        kernel_name=_kernel_name(notebook)
    )


def _update_execution_status(exe_id, name: str, status, params=None, errors=None):
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


def _update_execution_status_nb(exe_id, notebook: NotebookBasic, status, params=None, errors=None):
    return _update_execution_status(exe_id, notebook.fqn(), status, params, errors)
