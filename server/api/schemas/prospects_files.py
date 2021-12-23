from datetime import datetime
from typing import List, Optional

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

class ImportProspects(BaseModel):
    email_index: int
    first_name_index: int
    last_name_index: int
    force: Optional[bool]
    has_headers: Optional[bool]
