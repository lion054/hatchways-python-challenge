from typing import Union
from sqlalchemy.orm.session import Session
from api.models import ProspectFile


class ProspectFileCrud:
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
