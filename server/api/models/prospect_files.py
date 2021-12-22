from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import BigInteger, DateTime, Integer, String

from api.database import Base


class ProspectFile(Base):
    """Prospect Files Table"""

    __tablename__ = "prospect_files"

    id = Column(BigInteger, primary_key=True, autoincrement=True, unique=True)
    path = Column(String, nullable=False) # path of file
    total = Column(Integer, nullable=False) # total size of file
    done = Column(Integer, nullable=False) # processed size of file
    user_id = Column(BigInteger, ForeignKey("users.id"), primary_key=True) # who uploaded this file

    user = relationship("User", back_populates="prospect_files", foreign_keys=[user_id])

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"{self.id} | {self.path}"
