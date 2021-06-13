from typing import Optional, List

from pydantic import BaseModel

from src.model.jupyer_request import NotebookBasic
from src.model.message import Status


class SpaceBaseResponse(BaseModel):
    error: Optional[List[str]]
    info: Optional[List[str]]


class SpaceManagedResponse(SpaceBaseResponse):
    url: Optional[str]
    request_id: Optional[str]


class UpdateFromSpaceResponse(SpaceBaseResponse):
    request: Optional[NotebookBasic]
    status: Optional[Status]
