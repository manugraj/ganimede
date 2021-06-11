from typing import Optional, List

from pydantic import BaseModel


class SpaceManagedResponse(BaseModel):
    url: Optional[str]
    request_id: Optional[str]
    error: Optional[List[str]]
    info: Optional[List[str]]
