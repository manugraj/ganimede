from enum import Enum
from typing import Optional, TypeVar

from fastapi.requests import Request
from pydantic import BaseModel

Data = TypeVar("Data")


class Status(Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    STARTED = "STARTED"
    RUNNING = "RUNNING"


class Response(BaseModel):
    command: str
    status: Status
    info: Optional[str]
    data: Optional[Data]


def response(request: Request, status: bool, data=None, info: str = None):
    return Response(command=request.url.path, status=Status.SUCCESS if status else Status.FAILURE, data=data, info=info)
