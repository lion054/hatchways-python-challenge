from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class ProspectFile(BaseModel):
    id: int
    path: str
    total: int
    done: int
    created_at: datetime
    updated_at: datetime

class ProspectRow(BaseModel):
    email: str
    first_name: str
    last_name: str

class ProspectFileResponse(BaseModel):
    """One page of prospect files"""
    id: int
    preview: List[ProspectRow]

class ImportProspects(BaseModel):
    email_index: int
    first_name_index: int
    last_name_index: int
    force: Optional[bool]
    has_headers: Optional[bool]

class ProspectFileProgressResponse(BaseModel):
    total: int
    done: int
