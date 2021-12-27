from typing import List, Union
from sqlalchemy.orm.session import Session
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
            path = path,
            total = size,
            done = 0,
            user_id = user_id,
        )
        db.add(prospectFile)
        db.commit()
        db.refresh(prospectFile)
        return prospectFile

    @classmethod
    def get_by_id(cls, db: Session, file_id: int) -> Union[ProspectFile, None]:
        """Get a single prospect by id"""
        return db.query(ProspectFile).filter(ProspectFile.id == file_id).one_or_none()

    @classmethod
    def advance_importing_progress(cls, db: Session, file_id: int, done: int) -> Union[ProspectFile, None]:
        """Update a single prospect by id"""
        return db.query(ProspectFile).filter(ProspectFile.id == file_id).update({
            ProspectFile.done: done
        })

    @classmethod
    def delete_prospect_file(cls, db: Session, file_id: int) -> Union[ProspectFile, None]:
        """Delete a single prospect by id"""
        return db.query(ProspectFile).filter(ProspectFile.id == file_id).delete()
