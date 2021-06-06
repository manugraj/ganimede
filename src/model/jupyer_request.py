from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from src.model.message import Status


class Parameters(BaseModel):
    data: Optional[dict]


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
