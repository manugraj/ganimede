from src.storage.cache import Cache


class JupyterStore(Cache):
    def data_prefix(self) -> str:
        return "jupyter-"


class JupyterExecutionStore(Cache):
    def data_prefix(self) -> str:
        return "execution-"

