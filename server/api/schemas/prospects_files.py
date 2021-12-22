from datetime import datetime
from typing import List

from pydantic import BaseModel
from api.schemas import Prospect


class ProspectFile(BaseModel):
    id: int
    path: str
    total: int
    done: int
    created_at: datetime
    updated_at: datetime


class ProspectFileResponse(BaseModel):
    """One page of prospect files"""

    id: int
    preview: List[Prospect]
