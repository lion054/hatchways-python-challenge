from typing import List, Set, Union
from sqlalchemy.orm.session import Session
from api import schemas
from api.models import Prospect
from api.core.constants import DEFAULT_PAGE_SIZE, DEFAULT_PAGE, MIN_PAGE, MAX_PAGE_SIZE


class ProspectCrud:
    @classmethod
    def get_users_prospects(
        cls,
        db: Session,
        user_id: int,
        page: int = DEFAULT_PAGE,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> Union[List[Prospect], None]:
        """Get user's prospects"""
        if page < MIN_PAGE:
            page = MIN_PAGE
        if page_size > MAX_PAGE_SIZE:
            page_size = MAX_PAGE_SIZE
        return (
            db.query(Prospect)
            .filter(Prospect.user_id == user_id)
            .offset(page * page_size)
            .limit(page_size)
            .all()
        )

    @classmethod
    def get_user_prospects_total(cls, db: Session, user_id: int) -> int:
        return db.query(Prospect).filter(Prospect.user_id == user_id).count()

    @classmethod
    def create_prospect(
        cls, db: Session, user_id: int, data: schemas.ProspectCreate
    ) -> Prospect:
        """Create a prospect"""
        prospect = Prospect(**data, user_id=user_id)
        db.add(prospect)
        db.commit()
        db.refresh(prospect)
        return prospect

    @classmethod
    def import_prospect(
        cls, db: Session, user_id: int, data: schemas.ProspectCreate, force: bool
    ) -> Prospect:
        """Create or update a prospect"""
        exists = db.query(Prospect).filter(Prospect.user_id == user_id and Prospect.email == data.email).first() is not None
        if not exists:
            prospect = Prospect(**data, user_id = user_id)
            db.add(prospect)
            db.commit()
            db.refresh(prospect)
        elif force:
            id = db.query(Prospect).filter(Prospect.user_id == user_id and Prospect.email == data.email).update({
                Prospect.first_name: data.first_name,
                Prospect.last_name: data.last_name
            })
            db.commit()
            prospect = db.query(Prospect).filter(Prospect.id == id).one_or_none()
        return prospect

    @classmethod
    def validate_prospect_ids(
        cls, db: Session, user_id: int, unvalidated_prospect_ids: Set[int]
    ) -> Set[int]:
        res = (
            db.query(Prospect.id)
            .filter(
                Prospect.user_id == user_id, Prospect.id.in_(unvalidated_prospect_ids)
            )
            .all()
        )
        return {row.id for row in res}
