import os

from dotenv import load_dotenv
from loguru import logger

is_env_file = os.getenv("CONFIG_SOURCE", "env_file") == "env_file"


class SystemConfig:
    __loaded: bool = False

    @staticmethod
    def load():
        logger.info("Loading from env file: {}", is_env_file)
        if is_env_file:
            logger.info("Loading from env file: ganimede.env")
            from dotenv import find_dotenv
            load_dotenv(find_dotenv(filename='ganimede.env', raise_error_if_not_found=True))
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
    NOTEBOOK_STORE = "notebooks"
    NOTEBOOK_OUTPUT = "output"
    ENVIRONMENTS = "environments"
    DEFAULT_OUT_FILE = "output.ipynb"
    DEFAULT_OUT_FILE_NAME = "output"
    DEFAULT_STDOUT_FILE = "stdout.text"
    CONTAINER_DEFAULT = "spaces"
    CONTAINER_NB_DEFAULT = "nb"
