from src.model.jupyer_request import NotebookVersions
from src.storage.cache import Cache


class JupyterStore(Cache):
    def data_prefix(self) -> str:
        return "jupyter-"


class JupyterExecutionStore(Cache):
    def data_prefix(self) -> str:
        return "execution-"


class NotebookData(Cache):

    def data_prefix(self) -> str:
        return "nb-data-"

    def add_version(self, name, version, requirements) -> bool:
        data: NotebookVersions = self.get(name, NotebookVersions(name=name, versions={}))
        old_data: dict = data.versions or {}
        old_data[version] = requirements
        data.versions = old_data
        return self.put(name, data)

    def get_data(self, name, version):
        versions = self.get(name, NotebookVersions(name=name, versions={})).versions or {}
        return versions.get(version, {})

    def get_version(self, name):
        return self.get(name, NotebookVersions(name=name, versions={})).versions or {}


class EnvData(Cache):

    def data_prefix(self) -> str:
        return "env-data-"


class RequestStore(Cache):

    def data_prefix(self) -> str:
        return "request-store-data"
