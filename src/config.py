import os
import pathlib

from dotenv import load_dotenv
from loguru import logger

from src.utils.path_utils import paths

is_env_file = os.getenv("CONFIG_SOURCE", "env_file") == "env_file"
ROOT_DIR = None


class SystemConfig:
    __loaded: bool = False
    ROOT_DIR: str

    @staticmethod
    def load():
        logger.info("Loading from env file: {}", is_env_file)
        if is_env_file:
            logger.info("Loading from env file: ganimede.env")
            from dotenv import find_dotenv
            load_dotenv(find_dotenv(filename='ganimede.env', raise_error_if_not_found=True))
        SystemConfig.ROOT_DIR = str(pathlib.Path(os.getenv("GANIMEDE_PATH", "./orbit")).absolute())
        Constants.load()
        SystemConfig.__loaded = True

    @staticmethod
    def get(key: str, default=None):
        if not SystemConfig.__loaded and is_env_file:
            SystemConfig.load()
        return os.getenv(key, default)

    @staticmethod
    def get_vital(key: str):
        if not SystemConfig.__loaded:
            SystemConfig.load()
        env_val = os.getenv(key)
        if env_val:
            return env_val
        raise Exception(f"Mandatory parameter: {key} not available in env | Env file read: {is_env_file} ")


class Constants:
    NOTEBOOK_STORE: str
    NOTEBOOK_OUTPUT: str
    ENVIRONMENTS: str
    CONTAINER_DEFAULT: str
    CONTAINER_NB_DEFAULT: str
    DEFAULT_OUT_FILE = "output.ipynb"
    DEFAULT_OUT_FILE_NAME = "output"
    DEFAULT_STDOUT_FILE = "stdout.text"

    @staticmethod
    def load():
        Constants.NOTEBOOK_STORE = paths(SystemConfig.ROOT_DIR, "notebooks")
        Constants.NOTEBOOK_OUTPUT = paths(SystemConfig.ROOT_DIR, "output")
        Constants.ENVIRONMENTS = paths(SystemConfig.ROOT_DIR, "environments")
        Constants.CONTAINER_DEFAULT = paths(SystemConfig.ROOT_DIR, "spaces")
        Constants.CONTAINER_NB_DEFAULT = paths(Constants.CONTAINER_DEFAULT, "nb")
