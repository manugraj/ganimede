from enum import Enum
from typing import Optional

from fastapi.requests import Request
from pydantic import BaseModel


class Status(Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    STARTED = "STARTED"
    RUNNING = "RUNNING"


class Response(BaseModel):
    command: str
    status: Status
    info: Optional[str]


def response(request: Request, status: bool, info: str = None):
    return Response(command=request.url.path, status=Status.SUCCESS if status else Status.FAILURE, info=info)
