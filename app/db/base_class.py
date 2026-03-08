from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    @declared_attr
    # Now automatically each model will have table name which would be the filename in lowercase
    def __tablename__(cls):
        return cls.__name__.lower()

    # Each table will also have an id
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())