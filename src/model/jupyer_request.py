from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field

from src.model.message import Status


class Execution(BaseModel):
    exe_id: str
    completed_by: Optional[datetime]
    status: Optional[Status]
    started_at: Optional[datetime]
    parameters: Optional[dict]
    errors: Optional[List[str]]


class ExecutionStatus(BaseModel):
    name: str
    latest_status: Optional[Status]
    latest_output: Optional[str]
    latest_execution: Optional[str]
    executions: Optional[dict]


class DependencyLog(BaseModel):
    requirements: Optional[dict]
    dependency_versions: Optional[List[int]]


class NotebookBasic(BaseModel):
    name: str
    version: int = Field(default=1)

    def fqn(self):
        return f'{self.name}_v{self.version}'


class NotebookExecutionRequest(NotebookBasic):
    exe_id: Optional[str]
    parameters: Optional[dict]


class Notebook(NotebookBasic):
    dependency_log: Optional[DependencyLog]


class NotebookVersions(BaseModel):
    name: Optional[str]
    versions: Optional[dict]


class NotebookUpdate(BaseModel):
    base_nb: NotebookBasic
    new_version: int
    request_id: str
