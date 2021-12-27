from fastapi import File, UploadFile
from typing import List, Set, Union
from sqlalchemy.orm.session import Session
from api import schemas
from api.models import ProspectFile
from api.core.constants import DEFAULT_PAGE_SIZE, DEFAULT_PAGE, MIN_PAGE, MAX_PAGE_SIZE


class ProspectFileCrud:
    @classmethod
    def get_users_prospect_files(
        cls,
        db: Session,
        user_id: int,
        page: int = DEFAULT_PAGE,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> Union[List[ProspectFile], None]:
        """Get user's prospects"""
        if page < MIN_PAGE:
            page = MIN_PAGE
        if page_size > MAX_PAGE_SIZE:
            page_size = MAX_PAGE_SIZE
        return (
            db.query(ProspectFile)
            .filter(ProspectFile.user_id == user_id)
            .offset(page * page_size)
            .limit(page_size)
            .all()
        )

    @classmethod
    def create_prospect_file(
        cls, db: Session, user_id: int, path: str, size: int
    ) -> ProspectFile:
        """Create a prospect file"""
        prospectFile = ProspectFile(
            path=path,
            total=size,
            done=0,
            user_id=user_id,
        )
        db.add(prospectFile)
        db.commit()
        db.refresh(prospectFile)
        return prospectFile
